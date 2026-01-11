#ifndef AUDIOHANDLER_H
#define AUDIOHANDLER_H

#include <string>
#include <map>
#include <vector>
#include <memory>

struct TrackTags {
    std::string filename;
    std::string title;
    std::string artist;
    std::string album;
    std::string albumArtist;
    std::string year;
    std::string genre;
    std::string path;
    std::string lyrics;
    int coverStatus;  // 0=none, 1=exists, 2=500x500
    int lyricsStatus; // 0=none, 1=unsynced, 2=synced
    double duration;
};

class AudioHandler {
public:
    AudioHandler();
    ~AudioHandler();

    TrackTags getTags(const std::string& filepath);
    bool saveTags(const std::string& filepath, const TrackTags& tags);
    std::vector<unsigned char> getCover(const std::string& filepath);
    bool setCover(const std::string& filepath, const std::vector<unsigned char>& imageData, const std::string& mimeType = "image/jpeg");
    std::string getLyrics(const std::string& filepath);
    bool saveLyrics(const std::string& filepath, const std::string& lyrics);

private:
    int checkCoverStatus(const std::vector<unsigned char>& imageData);
    int checkLyricsStatus(const std::string& lyrics);
};

#endif // AUDIOHANDLER_H
