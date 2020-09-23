# attendance_app
## Usage
#### Visit all lessons one time
```
python main.py visit
```
#### Scrape today's schedule
```
python main.py scrape
```
Output will be writed into schedule.json 

#### Activate bot
Run bot in headless session
```
python main.py bot_1
```
Run bot in interactive session
```
python main.py bot_0
```

## Installation
Install python dependencies
```
pip install invoke
inv install
```
Setup geckodriver on linux. If you are using windows, skip this part.
```
export GECKO_DRIVER_VERSION='v0.24.0'
wget https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz
tar -xvzf geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz
rm geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz
chmod +x geckodriver
cp geckodriver /usr/local/bin/
```

## Setup
Insert your credentials into credentials.json file
