#ifndef CONFIGMANAGER_H
#define CONFIGMANAGER_H

#include <string>
#include <map>
#include <json/json.h>

class ConfigManager {
public:
    ConfigManager();
    ~ConfigManager();

    std::string get(const std::string& section, const std::string& key, const std::string& defaultValue = "");
    bool getBool(const std::string& section, const std::string& key, bool defaultValue = false);
    void set(const std::string& section, const std::string& key, const std::string& value);
    void setBool(const std::string& section, const std::string& key, bool value);
    bool save();
    bool load();

private:
    std::string configPath;
    Json::Value config;
};

#endif // CONFIGMANAGER_H
