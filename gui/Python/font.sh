sudo cp $(pwd)/SarasaUiTC-Regular.ttf /usr/local/share/fonts/
sudo fc-cache -fv
fc-list | grep "Sarasa"