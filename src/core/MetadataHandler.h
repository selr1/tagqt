#ifndef METADATAHANDLER_H
#define METADATAHANDLER_H

#include <string>
#include <vector>
#include <map>

struct Release {
    std::string id;
    std::string title;
    std::string artist;
    std::string date;
    std::string country;
};

class MetadataHandler {
public:
    MetadataHandler();
    ~MetadataHandler();

    std::string fetchCover(const std::string& artist, const std::string& album);
    std::vector<Release> searchReleases(const std::string& artist, const std::string& album);
    std::vector<unsigned char> getCoverBytes(const std::string& mbid);
    std::vector<std::map<std::string, std::string>> searchLyrics(const std::string& artist, const std::string& title, const std::string& album);

private:
    std::string fetchFromItunes(const std::string& artist, const std::string& album);
    std::string fetchFromMusicBrainz(const std::string& artist, const std::string& album);
    std::string downloadMBCover(const std::string& mbid);
    std::vector<unsigned char> downloadToTemp(const std::string& url);
    
    std::string mbUrl;
    std::string coverUrl;
    std::string lrcUrl;
    std::map<std::string, std::string> headers;
};

#endif // METADATAHANDLER_H
