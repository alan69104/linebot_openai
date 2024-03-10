#!/usr/bin/env bash

# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
    echo "...Downloading Chrome"
    mkdir -p $STORAGE_DIR/chrome
    cd $STORAGE_DIR/chrome
    wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
    rm ./google-chrome-stable_current_amd64.deb
    cd $HOME/project/src # Make sure we return to where we were
else
    echo "...Using Chrome from cache"
fi

# Download and install ChromeDriver
if [[ ! -f $STORAGE_DIR/chromedriver ]]; then
    echo "...Downloading ChromeDriver"
    wget -P $STORAGE_DIR https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.111/linux64/chromedriver-linux64.zip
    unzip -o $STORAGE_DIR/chromedriver-linux64.zip -d $STORAGE_DIR
    rm $STORAGE_DIR/chromedriver-linux64.zip
else
    echo "...Using ChromeDriver from cache"
fi

# be sure to add Chromes location to the PATH as part of your Start Command
export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome"
export PATH="${PATH}:/opt/render/project/.render/chromedriver-linux64"

/opt/render/project/.render/chrome/opt/google/chrome/chrome --version
/opt/render/project/.render/chromedriver-linux64/chromedriver --version

# add your own build commands...
# add your own build commands...
