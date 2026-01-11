#include "MetadataHandler.h"
#include "ConfigManager.h"
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QUrl>
#include <QUrlQuery>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QEventLoop>
#include <QTemporaryFile>
#include <QDir>
#include <iostream>

MetadataHandler::MetadataHandler() {
    mbUrl = "https://musicbrainz.org/ws/2";
    coverUrl = "https://coverartarchive.org";
    lrcUrl = "https://lrclib.net/api";
    headers["User-Agent"] = "TagFix/1.0 (https://github.com/tagfix)";
}

MetadataHandler::~MetadataHandler() {}

std::string MetadataHandler::fetchCover(const std::string& artist, const std::string& album) {
    ConfigManager config;
    std::string source = config.get("covers", "source", "iTunes");
    
    if (source == "iTunes") {
        std::string url = fetchFromItunes(artist, album);
        if (!url.empty()) {
            std::vector<unsigned char> data = downloadToTemp(url);
            if (!data.empty()) {
                // Write to temp file
                QTemporaryFile tempFile;
                tempFile.setAutoRemove(false);
                if (tempFile.open()) {
                    tempFile.write((const char*)data.data(), data.size());
                    tempFile.close();
                    return tempFile.fileName().toStdString();
                }
            }
        }
        
        std::cout << "iTunes failed, falling back to MusicBrainz..." << std::endl;
        return fetchFromMusicBrainz(artist, album);
    } else {
        std::string path = fetchFromMusicBrainz(artist, album);
        if (!path.empty()) return path;
        
        std::cout << "MusicBrainz failed, falling back to iTunes..." << std::endl;
        std::string url = fetchFromItunes(artist, album);
        if (!url.empty()) {
            std::vector<unsigned char> data = downloadToTemp(url);
            if (!data.empty()) {
                QTemporaryFile tempFile;
                tempFile.setAutoRemove(false);
                if (tempFile.open()) {
                    tempFile.write((const char*)data.data(), data.size());
                    tempFile.close();
                    return tempFile.fileName().toStdString();
                }
            }
        }
    }
    
    return "";
}

std::string MetadataHandler::fetchFromItunes(const std::string& artist, const std::string& album) {
    QNetworkAccessManager manager;
    
    QString term = QString::fromStdString(artist + " " + album);
    QUrl url("https://itunes.apple.com/search");
    QUrlQuery query;
    query.addQueryItem("term", term);
    query.addQueryItem("entity", "album");
    query.addQueryItem("limit", "1");
    url.setQuery(query);
    
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::UserAgentHeader, "TagFix/1.0");
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonDocument doc = QJsonDocument::fromJson(response);
        QJsonObject obj = doc.object();
        
        if (obj.contains("resultCount") && obj["resultCount"].toInt() > 0) {
            QJsonArray results = obj["results"].toArray();
            QJsonObject firstResult = results[0].toObject();
            
            if (firstResult.contains("artworkUrl100")) {
                QString artwork = firstResult["artworkUrl100"].toString();
                
                ConfigManager config;
                bool force500 = config.getBool("covers", "force_500px", true);
                
                if (force500) {
                    artwork.replace("100x100bb", "500x500bb");
                } else {
                    artwork.replace("100x100bb", "1000x1000bb");
                }
                
                reply->deleteLater();
                return artwork.toStdString();
            }
        }
    }
    
    reply->deleteLater();
    return "";
}

std::string MetadataHandler::fetchFromMusicBrainz(const std::string& artist, const std::string& album) {
    QNetworkAccessManager manager;
    
    QString query = QString("artist:\"%1\" AND release:\"%2\"")
        .arg(QString::fromStdString(artist))
        .arg(QString::fromStdString(album));
    
    QUrl url(QString::fromStdString(mbUrl) + "/release");
    QUrlQuery urlQuery;
    urlQuery.addQueryItem("query", query);
    urlQuery.addQueryItem("fmt", "json");
    urlQuery.addQueryItem("limit", "1");
    url.setQuery(urlQuery);
    
    QNetworkRequest request(url);
    request.setRawHeader("User-Agent", headers["User-Agent"].c_str());
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonDocument doc = QJsonDocument::fromJson(response);
        QJsonObject obj = doc.object();
        
        if (obj.contains("releases")) {
            QJsonArray releases = obj["releases"].toArray();
            if (!releases.isEmpty()) {
                QString mbid = releases[0].toObject()["id"].toString();
                reply->deleteLater();
                return downloadMBCover(mbid.toStdString());
            }
        }
    }
    
    reply->deleteLater();
    return "";
}

std::string MetadataHandler::downloadMBCover(const std::string& mbid) {
    ConfigManager config;
    bool force500 = config.getBool("covers", "force_500px", true);
    std::string suffix = force500 ? "front-500" : "front";
    
    QString coverUrlStr = QString::fromStdString(coverUrl) + "/release/" + 
                          QString::fromStdString(mbid) + "/" + QString::fromStdString(suffix);
    
    QNetworkAccessManager manager;
    QUrl url{coverUrlStr};
    QNetworkRequest request{url};
    request.setRawHeader("User-Agent", headers["User-Agent"].c_str());
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray imageData = reply->readAll();
        QTemporaryFile tempFile;
        tempFile.setAutoRemove(false);
        tempFile.setFileTemplate(QDir::tempPath() + "/tagfix_XXXXXX.jpg");
        
        if (tempFile.open()) {
            tempFile.write(imageData);
            tempFile.close();
            reply->deleteLater();
            return tempFile.fileName().toStdString();
        }
    } else if (force500 && reply->error() == QNetworkReply::ContentNotFoundError) {
        // Fallback to original size
        reply->deleteLater();
        coverUrlStr = QString::fromStdString(coverUrl) + "/release/" + 
                      QString::fromStdString(mbid) + "/front";
        
        QUrl fallbackUrl{coverUrlStr};
        request.setUrl(fallbackUrl);
        reply = manager.get(request);
        QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
        loop.exec();
        
        if (reply->error() == QNetworkReply::NoError) {
            QByteArray imageData = reply->readAll();
            QTemporaryFile tempFile;
            tempFile.setAutoRemove(false);
            tempFile.setFileTemplate(QDir::tempPath() + "/tagfix_XXXXXX.jpg");
            
            if (tempFile.open()) {
                tempFile.write(imageData);
                tempFile.close();
                reply->deleteLater();
                return tempFile.fileName().toStdString();
            }
        }
    }
    
    reply->deleteLater();
    return "";
}

std::vector<unsigned char> MetadataHandler::downloadToTemp(const std::string& url) {
    QNetworkAccessManager manager;
    QNetworkRequest request(QUrl(QString::fromStdString(url)));
    request.setRawHeader("User-Agent", headers["User-Agent"].c_str());
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    std::vector<unsigned char> data;
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        data.assign(response.begin(), response.end());
    }
    
    reply->deleteLater();
    return data;
}

std::vector<Release> MetadataHandler::searchReleases(const std::string& artist, const std::string& album) {
    std::vector<Release> releases;
    
    QNetworkAccessManager manager;
    QString query = QString("artist:\"%1\" AND release:\"%2\"")
        .arg(QString::fromStdString(artist))
        .arg(QString::fromStdString(album));
    
    QUrl url(QString::fromStdString(mbUrl) + "/release");
    QUrlQuery urlQuery;
    urlQuery.addQueryItem("query", query);
    urlQuery.addQueryItem("fmt", "json");
    urlQuery.addQueryItem("limit", "10");
    url.setQuery(urlQuery);
    
    QNetworkRequest request(url);
    request.setRawHeader("User-Agent", headers["User-Agent"].c_str());
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonDocument doc = QJsonDocument::fromJson(response);
        QJsonObject obj = doc.object();
        
        if (obj.contains("releases")) {
            QJsonArray releasesArray = obj["releases"].toArray();
            for (const QJsonValue &val : releasesArray) {
                QJsonObject releaseObj = val.toObject();
                Release r;
                r.id = releaseObj["id"].toString().toStdString();
                r.title = releaseObj["title"].toString().toStdString();
                r.date = releaseObj["date"].toString().toStdString();
                r.country = releaseObj["country"].toString().toStdString();
                
                if (releaseObj.contains("artist-credit")) {
                    QJsonArray artists = releaseObj["artist-credit"].toArray();
                    if (!artists.isEmpty()) {
                        r.artist = artists[0].toObject()["artist"].toObject()["name"].toString().toStdString();
                    }
                }
                
                releases.push_back(r);
            }
        }
    }
    
    reply->deleteLater();
    return releases;
}

std::vector<unsigned char> MetadataHandler::getCoverBytes(const std::string& mbid) {
    ConfigManager config;
    bool force500 = config.getBool("covers", "force_500px", true);
    std::string suffix = force500 ? "front-500" : "front";
    
    QString coverUrlStr = QString::fromStdString(coverUrl) + "/release/" + 
                          QString::fromStdString(mbid) + "/" + QString::fromStdString(suffix);
    
    QNetworkAccessManager manager;
    QUrl url{coverUrlStr};
    QNetworkRequest request{url};
    request.setRawHeader("User-Agent", headers["User-Agent"].c_str());
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    std::vector<unsigned char> data;
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray imageData = reply->readAll();
        data.assign(imageData.begin(), imageData.end());
    } else if (force500 && reply->error() == QNetworkReply::ContentNotFoundError) {
        // Fallback
        reply->deleteLater();
        coverUrlStr = QString::fromStdString(coverUrl) + "/release/" + 
                      QString::fromStdString(mbid) + "/front";
        
        QUrl fallbackUrl{coverUrlStr};
        request.setUrl(fallbackUrl);
        reply = manager.get(request);
        QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
        loop.exec();
        
        if (reply->error() == QNetworkReply::NoError) {
            QByteArray imageData = reply->readAll();
            data.assign(imageData.begin(), imageData.end());
        }
    }
    
    reply->deleteLater();
    return data;
}

std::vector<std::map<std::string, std::string>> MetadataHandler::searchLyrics(
    const std::string& artist, const std::string& title, const std::string& album) {
    
    std::vector<std::map<std::string, std::string>> results;
    
    QNetworkAccessManager manager;
    QString searchTerm = QString::fromStdString(artist + " " + title + " " + album).trimmed();
    
    QUrl url(QString::fromStdString(lrcUrl) + "/search");
    QUrlQuery query;
    query.addQueryItem("q", searchTerm);
    url.setQuery(query);
    
    QNetworkRequest request(url);
    request.setRawHeader("User-Agent", headers["User-Agent"].c_str());
    
    QNetworkReply *reply = manager.get(request);
    QEventLoop loop;
    QObject::connect(reply, &QNetworkReply::finished, &loop, &QEventLoop::quit);
    loop.exec();
    
    if (reply->error() == QNetworkReply::NoError) {
        QByteArray response = reply->readAll();
        QJsonDocument doc = QJsonDocument::fromJson(response);
        
        if (doc.isArray()) {
            QJsonArray arr = doc.array();
            for (const QJsonValue &val : arr) {
                QJsonObject obj = val.toObject();
                std::map<std::string, std::string> result;
                
                result["artist"] = obj["artistName"].toString().toStdString();
                result["title"] = obj["trackName"].toString().toStdString();
                result["album"] = obj["albumName"].toString().toStdString();
                result["plainLyrics"] = obj["plainLyrics"].toString().toStdString();
                result["syncedLyrics"] = obj["syncedLyrics"].toString().toStdString();
                
                results.push_back(result);
            }
        }
    }
    
    reply->deleteLater();
    return results;
}
