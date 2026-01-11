#include "ConfigManager.h"
#include <fstream>
#include <filesystem>
#include <iostream>

ConfigManager::ConfigManager() {
    // Use settings.json in current directory
    configPath = "settings.json";
    load();
}

ConfigManager::~ConfigManager() {}

std::string ConfigManager::get(const std::string& section, const std::string& key, const std::string& defaultValue) {
    if (config.isMember(section) && config[section].isMember(key)) {
        return config[section][key].asString();
    }
    return defaultValue;
}

bool ConfigManager::getBool(const std::string& section, const std::string& key, bool defaultValue) {
    if (config.isMember(section) && config[section].isMember(key)) {
        return config[section][key].asBool();
    }
    return defaultValue;
}

void ConfigManager::set(const std::string& section, const std::string& key, const std::string& value) {
    if (!config.isMember(section)) {
        config[section] = Json::Value(Json::objectValue);
    }
    config[section][key] = value;
}

void ConfigManager::setBool(const std::string& section, const std::string& key, bool value) {
    if (!config.isMember(section)) {
        config[section] = Json::Value(Json::objectValue);
    }
    config[section][key] = value;
}

bool ConfigManager::save() {
    try {
        std::ofstream file(configPath);
        if (!file.is_open()) {
            return false;
        }
        
        Json::StreamWriterBuilder builder;
        builder["indentation"] = "  ";
        std::unique_ptr<Json::StreamWriter> writer(builder.newStreamWriter());
        writer->write(config, &file);
        file.close();
        
        return true;
    } catch (...) {
        return false;
    }
}

bool ConfigManager::load() {
    try {
        if (!std::filesystem::exists(configPath)) {
            // Create default config
            config = Json::Value(Json::objectValue);
            config["covers"]["source"] = "iTunes";
            config["covers"]["force_500px"] = true;
            config["lyrics"]["auto_fetch"] = false;
            save();
            return true;
        }
        
        std::ifstream file(configPath);
        if (!file.is_open()) {
            return false;
        }
        
        Json::CharReaderBuilder builder;
        std::string errs;
        
        if (!Json::parseFromStream(builder, file, &config, &errs)) {
            std::cerr << "Error parsing config: " << errs << std::endl;
            return false;
        }
        
        file.close();
        return true;
    } catch (...) {
        return false;
    }
}
