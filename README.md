

# Environment setup

OSX 10.14.x (Mojave)
https://opensource.com/article/19/5/python-3-default-mac
https://pipenv-fork.readthedocs.io/en/latest/install.html
http://agiletesting.blogspot.com/2005/08/managing-dns-zone-files-with-dnspython.html

## Install homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew update

## Install python
brew install python
brew install pyenv
brew install pipenv
pyenv install 3.8.2
pyenv global 3.8.2
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
source ~/.bash_profile

## Start the environment

pipenv shell

## Build dependencies

pipenv install

## File cleanup

Any entries in the form of "CNAME 1 <VALUE>" cannot be parsed by dnspython and must be removed from the file first.

## Run the script against a file for domain ul.com

Example:
pipenv run python main.py -i input/my.zonefile.txt -d mydomain.com

## Results

You should get a csv file in the output folder. A progress bar and any error will be output to the screen.

