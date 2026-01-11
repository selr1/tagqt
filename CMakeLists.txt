cmake_minimum_required(VERSION 3.16)
project(TagFix VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Find required packages
find_package(Qt5 COMPONENTS Core Widgets Network REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(TAGLIB REQUIRED taglib)
pkg_check_modules(JSONCPP REQUIRED jsoncpp)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/src
    ${TAGLIB_INCLUDE_DIRS}
    ${JSONCPP_INCLUDE_DIRS}
)

# Source files
set(SOURCES
    src/main.cpp
    src/core/AudioHandler.cpp
    src/core/MetadataHandler.cpp
    src/core/ConfigManager.cpp
    src/gui/MainWindow.cpp
    src/gui/TrackTable.cpp
    src/gui/EditorPanel.cpp
    src/gui/BrowserPanel.cpp
    src/gui/dialogs/CoverSearchDialog.cpp
    src/gui/dialogs/LyricsSearchDialog.cpp
    src/gui/dialogs/SettingsDialog.cpp
    src/gui/dialogs/BatchEditDialog.cpp
)

set(HEADERS
    src/core/AudioHandler.h
    src/core/MetadataHandler.h
    src/core/ConfigManager.h
    src/gui/MainWindow.h
    src/gui/TrackTable.h
    src/gui/EditorPanel.h
    src/gui/BrowserPanel.h
    src/gui/dialogs/CoverSearchDialog.h
    src/gui/dialogs/LyricsSearchDialog.h
    src/gui/dialogs/SettingsDialog.h
    src/gui/dialogs/BatchEditDialog.h
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# Link libraries
target_link_libraries(${PROJECT_NAME}
    Qt5::Core
    Qt5::Widgets
    Qt5::Network
    ${TAGLIB_LIBRARIES}
    ${JSONCPP_LIBRARIES}
)

# Installation
install(TARGETS ${PROJECT_NAME} DESTINATION bin)
