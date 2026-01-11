#include "AudioHandler.h"
#include <taglib/fileref.h>
#include <taglib/tag.h>
#include <taglib/tpropertymap.h>
#include <taglib/mpegfile.h>
#include <taglib/id3v2tag.h>
#include <taglib/id3v2frame.h>
#include <taglib/attachedpictureframe.h>
#include <taglib/unsynchronizedlyricsframe.h>
#include <taglib/flacfile.h>
#include <taglib/flacpicture.h>
#include <taglib/mp4file.h>
#include <taglib/mp4tag.h>
#include <taglib/mp4coverart.h>
#include <filesystem>
#include <fstream>
#include <regex>

AudioHandler::AudioHandler() {}

AudioHandler::~AudioHandler() {}

TrackTags AudioHandler::getTags(const std::string& filepath) {
    TrackTags tags;
    tags.filename = std::filesystem::path(filepath).filename().string();
    tags.path = filepath;
    tags.coverStatus = 0;
    tags.lyricsStatus = 0;
    tags.duration = 0.0;

    try {
        TagLib::FileRef f(filepath.c_str());
        
        if (!f.isNull() && f.tag()) {
            TagLib::Tag *tag = f.tag();
            tags.title = tag->title().toCString(true);
            tags.artist = tag->artist().toCString(true);
            tags.album = tag->album().toCString(true);
            tags.year = std::to_string(tag->year());
            if (tags.year == "0") tags.year = "";
            tags.genre = tag->genre().toCString(true);
            
            // Get album artist from properties
            TagLib::PropertyMap props = f.file()->properties();
            if (props.contains("ALBUMARTIST")) {
                tags.albumArtist = props["ALBUMARTIST"].front().toCString(true);
            }
            
            // Get duration
            if (f.audioProperties()) {
                tags.duration = f.audioProperties()->length();
            }
        }

        // Get cover and lyrics for MP3
        if (filepath.substr(filepath.length() - 4) == ".mp3") {
            TagLib::MPEG::File mp3File(filepath.c_str());
            if (mp3File.isValid() && mp3File.ID3v2Tag()) {
                TagLib::ID3v2::Tag *id3v2 = mp3File.ID3v2Tag();
                
                // Check for cover
                TagLib::ID3v2::FrameList frames = id3v2->frameListMap()["APIC"];
                if (!frames.isEmpty()) {
                    TagLib::ID3v2::AttachedPictureFrame *frame = 
                        static_cast<TagLib::ID3v2::AttachedPictureFrame*>(frames.front());
                    std::vector<unsigned char> imageData(frame->picture().data(), 
                                                        frame->picture().data() + frame->picture().size());
                    tags.coverStatus = checkCoverStatus(imageData);
                }
                
                // Check for lyrics
                TagLib::ID3v2::FrameList lyricsFrames = id3v2->frameListMap()["USLT"];
                if (!lyricsFrames.isEmpty()) {
                    TagLib::ID3v2::UnsynchronizedLyricsFrame *lyricsFrame = 
                        static_cast<TagLib::ID3v2::UnsynchronizedLyricsFrame*>(lyricsFrames.front());
                    tags.lyrics = lyricsFrame->text().toCString(true);
                    tags.lyricsStatus = checkLyricsStatus(tags.lyrics);
                }
            }
        }
        // Get cover and lyrics for FLAC
        else if (filepath.substr(filepath.length() - 5) == ".flac") {
            TagLib::FLAC::File flacFile(filepath.c_str());
            if (flacFile.isValid()) {
                // Check for cover
                TagLib::List<TagLib::FLAC::Picture*> pics = flacFile.pictureList();
                if (!pics.isEmpty()) {
                    TagLib::FLAC::Picture *pic = pics.front();
                    std::vector<unsigned char> imageData(pic->data().data(),
                                                        pic->data().data() + pic->data().size());
                    tags.coverStatus = checkCoverStatus(imageData);
                }
                
                // Check for lyrics
                if (flacFile.xiphComment()) {
                    TagLib::PropertyMap props = flacFile.properties();
                    if (props.contains("LYRICS")) {
                        tags.lyrics = props["LYRICS"].front().toCString(true);
                        tags.lyricsStatus = checkLyricsStatus(tags.lyrics);
                    }
                }
            }
        }

    } catch (...) {
        // Return partial tags on error
    }

    return tags;
}

bool AudioHandler::saveTags(const std::string& filepath, const TrackTags& tags) {
    try {
        TagLib::FileRef f(filepath.c_str());
        
        if (f.isNull() || !f.tag()) {
            return false;
        }

        TagLib::Tag *tag = f.tag();
        tag->setTitle(TagLib::String(tags.title, TagLib::String::UTF8));
        tag->setArtist(TagLib::String(tags.artist, TagLib::String::UTF8));
        tag->setAlbum(TagLib::String(tags.album, TagLib::String::UTF8));
        tag->setGenre(TagLib::String(tags.genre, TagLib::String::UTF8));
        
        if (!tags.year.empty()) {
            tag->setYear(std::stoi(tags.year));
        }

        // Set album artist
        if (!tags.albumArtist.empty()) {
            TagLib::PropertyMap props = f.file()->properties();
            props.replace("ALBUMARTIST", TagLib::StringList(TagLib::String(tags.albumArtist, TagLib::String::UTF8)));
            f.file()->setProperties(props);
        }

        f.save();

        // Handle lyrics separately for different formats
        if (!tags.lyrics.empty()) {
            saveLyrics(filepath, tags.lyrics);
        }

        return true;
    } catch (...) {
        return false;
    }
}

std::vector<unsigned char> AudioHandler::getCover(const std::string& filepath) {
    std::vector<unsigned char> imageData;

    try {
        if (filepath.substr(filepath.length() - 4) == ".mp3") {
            TagLib::MPEG::File mp3File(filepath.c_str());
            if (mp3File.isValid() && mp3File.ID3v2Tag()) {
                TagLib::ID3v2::FrameList frames = mp3File.ID3v2Tag()->frameListMap()["APIC"];
                if (!frames.isEmpty()) {
                    TagLib::ID3v2::AttachedPictureFrame *frame = 
                        static_cast<TagLib::ID3v2::AttachedPictureFrame*>(frames.front());
                    imageData.assign(frame->picture().data(),
                                   frame->picture().data() + frame->picture().size());
                }
            }
        } else if (filepath.substr(filepath.length() - 5) == ".flac") {
            TagLib::FLAC::File flacFile(filepath.c_str());
            if (flacFile.isValid()) {
                TagLib::List<TagLib::FLAC::Picture*> pics = flacFile.pictureList();
                if (!pics.isEmpty()) {
                    TagLib::FLAC::Picture *pic = pics.front();
                    imageData.assign(pic->data().data(),
                                   pic->data().data() + pic->data().size());
                }
            }
        } else if (filepath.substr(filepath.length() - 4) == ".m4a") {
            TagLib::MP4::File mp4File(filepath.c_str());
            if (mp4File.isValid() && mp4File.tag()) {
                TagLib::MP4::Tag *tag = mp4File.tag();
                if (tag->itemListMap().contains("covr")) {
                    TagLib::MP4::CoverArtList coverList = tag->itemListMap()["covr"].toCoverArtList();
                    if (!coverList.isEmpty()) {
                        imageData.assign(coverList.front().data().data(),
                                       coverList.front().data().data() + coverList.front().data().size());
                    }
                }
            }
        }
    } catch (...) {
        // Return empty vector on error
    }

    return imageData;
}

bool AudioHandler::setCover(const std::string& filepath, const std::vector<unsigned char>& imageData, const std::string& mimeType) {
    try {
        if (filepath.substr(filepath.length() - 4) == ".mp3") {
            TagLib::MPEG::File mp3File(filepath.c_str());
            if (mp3File.isValid()) {
                if (!mp3File.ID3v2Tag()) {
                    mp3File.ID3v2Tag(true);
                }
                
                TagLib::ID3v2::Tag *tag = mp3File.ID3v2Tag();
                
                // Remove existing covers
                tag->removeFrames("APIC");
                
                // Add new cover
                TagLib::ID3v2::AttachedPictureFrame *frame = new TagLib::ID3v2::AttachedPictureFrame();
                frame->setMimeType(TagLib::String(mimeType, TagLib::String::UTF8));
                frame->setPicture(TagLib::ByteVector((const char*)imageData.data(), imageData.size()));
                frame->setType(TagLib::ID3v2::AttachedPictureFrame::FrontCover);
                tag->addFrame(frame);
                
                mp3File.save();
                return true;
            }
        } else if (filepath.substr(filepath.length() - 5) == ".flac") {
            TagLib::FLAC::File flacFile(filepath.c_str());
            if (flacFile.isValid()) {
                flacFile.removePictures();
                
                TagLib::FLAC::Picture *pic = new TagLib::FLAC::Picture();
                pic->setType(TagLib::FLAC::Picture::FrontCover);
                pic->setMimeType(TagLib::String(mimeType, TagLib::String::UTF8));
                pic->setData(TagLib::ByteVector((const char*)imageData.data(), imageData.size()));
                
                flacFile.addPicture(pic);
                flacFile.save();
                return true;
            }
        } else if (filepath.substr(filepath.length() - 4) == ".m4a") {
            TagLib::MP4::File mp4File(filepath.c_str());
            if (mp4File.isValid()) {
                if (!mp4File.tag()) {
                    mp4File.tag();
                }
                
                TagLib::MP4::Tag *tag = mp4File.tag();
                TagLib::MP4::CoverArt::Format format = (mimeType == "image/jpeg") ? 
                    TagLib::MP4::CoverArt::JPEG : TagLib::MP4::CoverArt::PNG;
                    
                TagLib::MP4::CoverArt coverArt(format, 
                    TagLib::ByteVector((const char*)imageData.data(), imageData.size()));
                TagLib::MP4::CoverArtList coverList;
                coverList.append(coverArt);
                tag->itemListMap()["covr"] = coverList;
                
                mp4File.save();
                return true;
            }
        }
    } catch (...) {
        return false;
    }

    return false;
}

std::string AudioHandler::getLyrics(const std::string& filepath) {
    try {
        if (filepath.substr(filepath.length() - 4) == ".mp3") {
            TagLib::MPEG::File mp3File(filepath.c_str());
            if (mp3File.isValid() && mp3File.ID3v2Tag()) {
                TagLib::ID3v2::FrameList frames = mp3File.ID3v2Tag()->frameListMap()["USLT"];
                if (!frames.isEmpty()) {
                    TagLib::ID3v2::UnsynchronizedLyricsFrame *frame = 
                        static_cast<TagLib::ID3v2::UnsynchronizedLyricsFrame*>(frames.front());
                    return frame->text().toCString(true);
                }
            }
        } else if (filepath.substr(filepath.length() - 5) == ".flac") {
            TagLib::FLAC::File flacFile(filepath.c_str());
            if (flacFile.isValid() && flacFile.xiphComment()) {
                TagLib::PropertyMap props = flacFile.properties();
                if (props.contains("LYRICS")) {
                    return props["LYRICS"].front().toCString(true);
                }
            }
        } else if (filepath.substr(filepath.length() - 4) == ".m4a") {
            TagLib::MP4::File mp4File(filepath.c_str());
            if (mp4File.isValid() && mp4File.tag()) {
                if (mp4File.tag()->itemListMap().contains("\251lyr")) {
                    return mp4File.tag()->itemListMap()["\251lyr"].toStringList().front().toCString(true);
                }
            }
        }
    } catch (...) {
        // Return empty on error
    }

    return "";
}

bool AudioHandler::saveLyrics(const std::string& filepath, const std::string& lyrics) {
    try {
        if (filepath.substr(filepath.length() - 4) == ".mp3") {
            TagLib::MPEG::File mp3File(filepath.c_str());
            if (mp3File.isValid()) {
                if (!mp3File.ID3v2Tag()) {
                    mp3File.ID3v2Tag(true);
                }
                
                TagLib::ID3v2::Tag *tag = mp3File.ID3v2Tag();
                tag->removeFrames("USLT");
                
                if (!lyrics.empty()) {
                    TagLib::ID3v2::UnsynchronizedLyricsFrame *frame = 
                        new TagLib::ID3v2::UnsynchronizedLyricsFrame(TagLib::String::UTF8);
                    frame->setLanguage("eng");
                    frame->setText(TagLib::String(lyrics, TagLib::String::UTF8));
                    tag->addFrame(frame);
                }
                
                mp3File.save();
                return true;
            }
        } else if (filepath.substr(filepath.length() - 5) == ".flac") {
            TagLib::FLAC::File flacFile(filepath.c_str());
            if (flacFile.isValid()) {
                TagLib::PropertyMap props = flacFile.properties();
                if (!lyrics.empty()) {
                    props.replace("LYRICS", TagLib::StringList(TagLib::String(lyrics, TagLib::String::UTF8)));
                } else {
                    props.erase("LYRICS");
                }
                flacFile.setProperties(props);
                flacFile.save();
                return true;
            }
        } else if (filepath.substr(filepath.length() - 4) == ".m4a") {
            TagLib::MP4::File mp4File(filepath.c_str());
            if (mp4File.isValid()) {
                if (!mp4File.tag()) {
                    mp4File.tag();
                }
                
                TagLib::MP4::Tag *tag = mp4File.tag();
                if (!lyrics.empty()) {
                    tag->itemListMap()["\251lyr"] = TagLib::StringList(TagLib::String(lyrics, TagLib::String::UTF8));
                } else {
                    tag->itemListMap().erase("\251lyr");
                }
                
                mp4File.save();
                return true;
            }
        }
    } catch (...) {
        return false;
    }

    return false;
}

int AudioHandler::checkCoverStatus(const std::vector<unsigned char>& imageData) {
    // Check if cover exists
    // TODO: Could use QImage to check dimensions for status 2 (500x500)
    // For now: 0=no cover, 1=has cover, 2=perfect size (not implemented)
    return imageData.empty() ? 0 : 1;
}

int AudioHandler::checkLyricsStatus(const std::string& lyrics) {
    if (lyrics.empty()) return 0;
    
    // Check for timestamp pattern [mm:ss.xx] or [mm:ss]
    std::regex timestampPattern(R"(\[\d{2}:\d{2}(?:\.\d{2,3})?\])");
    if (std::regex_search(lyrics, timestampPattern)) {
        return 2; // Synced
    }
    
    return 1; // Unsynced
}
