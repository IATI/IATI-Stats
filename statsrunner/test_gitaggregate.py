import os
import imp
import shutil
import sys
from mock import patch


def test_gitaggregate(tmpdir):
    global statsrunner
    gitout = tmpdir.join('gitout')
    sys.argv = ['', '--dated']
    with patch.dict('os.environ', GITOUT_DIR=gitout.strpath):
        gitout.join('commits').join('AAA').join('aggregated').join('teststat.json').write('3', ensure=True)
        import statsrunner.gitaggregate
        assert gitout.join('gitaggregate').listdir() == [gitout.join('gitaggregate').join('teststat.json')]
        assert gitout.join('gitaggregate').join('teststat.json').read() == '{\n  "AAA": 3\n}'

        gitout.join('commits').join('BBB').join('aggregated').join('teststat.json').write('"test"', ensure=True)
        imp.reload(statsrunner.gitaggregate)
        assert gitout.join('gitaggregate').listdir() == [gitout.join('gitaggregate').join('teststat.json')]
        assert gitout.join('gitaggregate').join('teststat.json').read() == '{\n  "AAA": 3, \n  "BBB": "test"\n}'

        # Ensure that existing values are maintained once they are missing from the commits directory
        shutil.rmtree(gitout.join('commits').strpath)
        gitout.join('commits').join('CCC').join('aggregated').join('teststat.json').write('{}', ensure=True)
        imp.reload(statsrunner.gitaggregate)
        assert gitout.join('gitaggregate').listdir() == [gitout.join('gitaggregate').join('teststat.json')]
        assert gitout.join('gitaggregate').join('teststat.json').read() == '{\n  "AAA": 3, \n  "BBB": "test", \n  "CCC": {}\n}'


def test_gitaggregate_dated(tmpdir):
    global statsrunner
    gitout = tmpdir.join('gitout')
    sys.argv = ['', 'dated']
    with open('gitdate.json', 'w') as fp:
        fp.write('{"AAA":"1","BBB":"2","CCC":"3"}')
    with patch.dict('os.environ', GITOUT_DIR=gitout.strpath):
        gitout.join('commits').join('AAA').join('aggregated').join('teststat.json').write('3', ensure=True)
        imp.reload(statsrunner.gitaggregate)
        assert gitout.join('gitaggregate-dated').listdir() == [gitout.join('gitaggregate-dated').join('teststat.json')]
        assert gitout.join('gitaggregate-dated').join('teststat.json').read() == '{\n  "1": 3\n}'

        gitout.join('commits').join('BBB').join('aggregated').join('teststat.json').write('"test"', ensure=True)
        imp.reload(statsrunner.gitaggregate)
        assert gitout.join('gitaggregate-dated').listdir() == [gitout.join('gitaggregate-dated').join('teststat.json')]
        assert gitout.join('gitaggregate-dated').join('teststat.json').read() == '{\n  "1": 3, \n  "2": "test"\n}'

        # Ensure that existing values are maintained once they are missing from the commits directory
        shutil.rmtree(gitout.join('commits').strpath)
        gitout.join('commits').join('CCC').join('aggregated').join('teststat.json').write('{}', ensure=True)
        imp.reload(statsrunner.gitaggregate)
        assert gitout.join('gitaggregate-dated').listdir() == [gitout.join('gitaggregate-dated').join('teststat.json')]
        assert gitout.join('gitaggregate-dated').join('teststat.json').read() == '{\n  "1": 3, \n  "2": "test", \n  "3": {}\n}'

