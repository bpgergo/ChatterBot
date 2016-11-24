from io import BytesIO
import unittest
import tarfile
import os
from mock import Mock

from tests.base_case import ChatBotTestCase
from chatterbot.trainers import UbuntuCorpusTrainer


class UbuntuCorpusTrainerTestCase(ChatBotTestCase):
    """
    Test the Ubuntu Corpus trainer class.
    """

    def setUp(self):
        super(UbuntuCorpusTrainerTestCase, self).setUp()
        self.chatbot.set_trainer(UbuntuCorpusTrainer)

    def tearDown(self):
        super(UbuntuCorpusTrainerTestCase, self).tearDown()

        # Clean up by removing the corpus data directory
        os.removedirs(self.chatbot.trainer.data_directory)

    def _create_test_corpus(self):
        """
        Create a small tar in a similar format to the
        Ubuntu corpus file in memory for testing.
        """
        tar = tarfile.TarFile('ubuntu_corpus.tar', 'w')

        data1 = (
            b'2004-11-04T16:49:00.000Z	tom		jane : Hello\n' +
            b'2004-11-04T16:49:00.000Z	tom		jane : Is anyone there?\n' +
            b'2004-11-04T16:49:00.000Z	jane	tom	I am good' +
            b'\n'
        )

        data2 = (
            b'2004-11-04T16:49:00.000Z	tom		jane : Hello\n' +
            b'2004-11-04T16:49:00.000Z	tom		jane : Is anyone there?\n' +
            b'2004-11-04T16:49:00.000Z	jane	tom	I am good' +
            b'\n'
        )

        tsv1 = BytesIO(data1)
        tsv2 = BytesIO(data2)

        tarinfo = tarfile.TarInfo('ubuntu_dialogs/3/1.tsv')
        tarinfo.size = len(data1)
        tar.addfile(tarinfo, fileobj=tsv1)

        tarinfo = tarfile.TarInfo('ubuntu_dialogs/3/2.tsv')
        tarinfo.size = len(data2)
        tar.addfile(tarinfo, fileobj=tsv2)

        tsv1.close()
        tsv2.close()
        tar.close()

        return os.path.realpath(tar.name)

    def _mock_get_response(self, *args, **kwargs):
        """
        Return a requests.Response object.
        """
        import requests
        response = requests.Response()
        response._content = b'Some response content'
        response.headers['content-length'] = len(response.content)
        return response

    def test_download(self):
        """
        Test the download function for the Ubuntu corpus trainer.
        """
        import requests

        requests.get = Mock(side_effect=self._mock_get_response)
        download_url = 'https://example.com/download.tar'
        self.chatbot.trainer.download(download_url, show_status=False)

        file_name = download_url.split('/')[-1]
        downloaded_file_path = os.path.join(self.chatbot.trainer.data_directory, file_name)

        requests.get.assert_called_with(download_url, stream=True)
        self.assertTrue(os.path.exists(downloaded_file_path))

        # Remove the dummy download_url
        os.remove(downloaded_file_path)

    def test_download_file_exists(self):
        """
        Test the case that the corpus file exists.
        """
        import requests

        file_path = os.path.join(self.chatbot.trainer.data_directory, 'download.tar')
        open(file_path, 'a').close()

        requests.get = Mock(side_effect=self._mock_get_response)
        download_url = 'https://example.com/download.tar'
        self.chatbot.trainer.download(download_url, show_status=False)

        # Remove the dummy download_url
        os.remove(file_path)

        self.assertFalse(requests.get.called)

    def test_download_url_does_not_exist(self):
        """
        Test the case that the url being downloaded does not exist.
        """
        raise unittest.SkipTest('This test needs to be created.')

    def test_extract(self):
        """
        Test the extraction of text from a decompressed Ubuntu Corpus file.
        """
        file_object_path = self._create_test_corpus()
        self.chatbot.trainer.extract(file_object_path)

    def test_train(self):
        """
        Test that the chat bot is trained using data from the Ubuntu Corpus.
        """
        pass
