# MCSR Recording Tool Version 1.0

A tool for automatically starting and stopping recordings for MCSR games.

The tool removes the need to manually manage recordings and makes it easier to organise and manage your gameplay footage.

## Features

- 🎥 Automatically starts recording when an MCSR game begins
- ⏹️ Automatically stops recording when the game ends
- 📁 Automatically organises recorded videos
- 🏷️ Automatically generates video titles
- 💾 Saves your settings between sessions
- 🔧 Supports OBS Studio

## Requirements

- Windows
- OBS Studio
- Minecraft
- MCSR Ranked

## Quick Start Guide

### 1. Download the Executable

Download the latest `.exe` from the **Releases** page.

### 2. Open the App

Launch `MCSR Recording Tool.exe`.

### 3. Configure Settings

Open the **Settings** page and configure all settings:

- Minecraft Username
- Minecraft Log Directory (Will attempt to auto locate)
- Video Sorting
- Video Output Directory
- OBS Websocket settings
- Auto Open OBS (When start is pressed)
- OBS link directory (needs to be mapped to a .lnk)
- 
- API Key **CAN BE IGNORED*
### 4. Save Your Settings

Click **Save** to save your configuration.

### 5. Start Recording

Press **Start**.

The tool will monitor your MCSR game and automatically manage the recording.

## Video Organisation

Recordings can be automatically organised into folders based on the game information.

For example:

```text
Recordings/
├──Completed Runs/
│    ├── 2026-09-22/
│    │   └──  11-38 - Desert Temple.mp4
│    │   └── ...
