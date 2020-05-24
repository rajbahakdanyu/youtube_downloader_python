from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType

import sys
import pafy
import humanize
import os

ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.button()

    def button(self):
        # Handles all button functionality
        self.singleDownload.clicked.connect(self.single_download)
        self.singleBrowse.clicked.connect(self.single_browse)
        self.singleGet.clicked.connect(self.get_video_data)        
        self.playlistBrowse.clicked.connect(self.playlist_browse)
        self.playlistDownload.clicked.connect(self.playlist_download)

    # Single Video Download
    def single_progress(self, total, received, ratio, rate, time):
        # Handles progress bar
        read_data = received

        if total > 0:
            download_percentage = (read_data * 100) / total
            self.singleProgress.setValue(download_percentage)
            remaining_time = round(time/60, 2)
            self.singleTime.setText(str('{} minutes remaining'.format(remaining_time)))
            QApplication.processEvents()

    def single_browse(self):
        # Used to select save location
        save_location = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.singleSave.setText(str(save_location))

    def single_download(self):
        # Used to download files
        download_url = self.singleUrl.text()
        save_location = self.singleSave.text()

        if download_url == '' or save_location == '':
            QMessageBox.warning(self, 'Error', 'Please provide a valid youtube URL and save location.')
        else:
            video = pafy.new(download_url)
            video_stream = video.allstreams
            title = video.title
            video_quality = self.singleCombo.currentIndex()
            download = video_stream[video_quality].download(filepath=save_location, callback=self.single_progress)

    def get_video_data(self):
        # Getting data of youtube video
        single_video = self.singleUrl.text()

        if single_video == '':
            QMessageBox.warning(self, 'Invalid Link', 'Please provide a valid youtube URL.')
        else:
            video = pafy.new(single_video)

            video_streams = video.allstreams
            for stream in video_streams:
                size = humanize.naturalsize(stream.get_filesize())
                data = "Type: {}, Extension: {}, Quality: {}, Size: {}".format(stream.mediatype, stream.extension, stream.quality, size)
                self.singleCombo.addItem(data)

    # Playlist Download
    def playlist_download(self):
        playlist_url = self.playlistUrl.text()
        save_location = self.playlistSave.text()

        if playlist_url == '' or save_location == '':
            QMessageBox.warning(self, 'Error', 'Please provide a valid playlist URL and save location.')
        else:
            playlist = pafy.get_playlist(playlist_url)
            playlist_videos = playlist['items']

            os.chdir(save_location)
            if os.path.exists(str(playlist['title'])):
                os.chdir(str(playlist['title']))
            else:
                os.mkdir(str(playlist['title']))
                os.chdir(str(playlist['title']))

            current_video_number = 1

            self.currentLcd.display(current_video_number)
            self.fullLcd.display(len(playlist_videos))

            QApplication.processEvents()

            for video in playlist_videos:
                current_video = video['pafy']
                current_video_stream = current_video.getbest()
                download = current_video_stream.download(callback=self.playlist_progress)
                current_video_number += 1
                self.currentLcd.display(current_video_number)
                QApplication.processEvents()



    def playlist_progress(self, total, received, ratio, rate, time):
        read_data = received

        if total > 0:
            download_percentage = (read_data * 100) / total
            self.playlistProgress.setValue(download_percentage)
            remaining_time = round(time/60, 2)
            self.playlistTime.setText(str('{} minutes remaining'.format(remaining_time)))
            QApplication.processEvents()

    def playlist_browse(self):
        save_location = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.playlistSave.setText(str(save_location))


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
