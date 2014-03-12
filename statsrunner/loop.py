import os
from lxml import etree
import inspect
import json
import sys
import traceback
import decimal
import argparse
import statsrunner.shared
import statsrunner.aggregate

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def call_stats(this_stats, args):
    this_out = {}
    for name, function in inspect.getmembers(this_stats, predicate=inspect.ismethod):
        if not statsrunner.shared.use_stat(this_stats, name): continue
        try:
            this_out[name] = function()
        except KeyboardInterrupt:
            exit()
        except:
            traceback.print_exc(file=sys.stdout)
    if args.debug:
        print this_out
    return this_out


def process_file((inputfile, output_dir, folder, xmlfile, args)):
    import importlib
    stats_module = importlib.import_module(args.stats_module)
    
    if args.verbose_loop:
        try: os.makedirs(os.path.join(output_dir,'loop',folder))
        except OSError: pass
        outputfile = os.path.join(output_dir,'loop',folder,xmlfile)
    else:
        outputfile = os.path.join(output_dir,'aggregated-file',folder,xmlfile)

    if args.new:
        if os.path.exists(outputfile):
            return

    try:
        doc = etree.parse(inputfile)
        root = doc.getroot()
        def process_stats_file(FileStats):
            file_stats = FileStats()
            file_stats.doc = doc
            file_stats.root = root
            file_stats.strict = args.strict
            file_stats.context = 'in '+inputfile
            file_stats.fname = os.path.basename(inputfile)
            file_stats.inputfile = inputfile
            return call_stats(file_stats, args)

        def process_stats_element(ElementStats, tagname=None):
            for element in root:
                if tagname and tagname != element.tag: continue
                element_stats = ElementStats()
                element_stats.element = element
                element_stats.strict = args.strict
                element_stats.context = 'in '+inputfile
                yield call_stats(element_stats, args)

        def process_stats(FileStats, ElementStats, tagname=None):
            file_out = process_stats_file(FileStats)
            out = list(process_stats_element(ElementStats, tagname))
            return {'file':file_out, 'elements':out}

        if root.tag == 'iati-activities':
            stats_json = process_stats(stats_module.ActivityFileStats, stats_module.ActivityStats, 'iati-activity')
        elif root.tag == 'iati-organisations':
            stats_json = process_stats(stats_module.OrganisationFileStats, stats_module.OrganisationStats, 'iati-organisation')
        else:
            stats_json = {'file':{'nonstandardroots':1}, 'elements':[]}

    except etree.ParseError:
        print 'Could not parse file {0}'.format(inputfile)
        if os.path.getsize(inputfile) == 0:
            # Assume empty files are download errors, not invalid XML
            stats_json = {'file':{'emptyfile':1}, 'elements':[]}
        else:
            stats_json = {'file':{'invalidxml':1}, 'elements':[]}

    if args.verbose_loop:
        with open(outputfile, 'w') as outfp:
            json.dump(stats_json, outfp, sort_keys=True, indent=2, default=decimal_default)
    else:
        statsrunner.aggregate.aggregate_file(stats_module, stats_json, os.path.join(output_dir, 'aggregated-file', folder, xmlfile))


def loop_folder(folder, args, data_dir, output_dir):
    if not os.path.isdir(os.path.join(data_dir, folder)) or folder == '.git':
        return []
    files = []
    for xmlfile in os.listdir(os.path.join(data_dir, folder)):
        try:
            files.append((os.path.join(data_dir,folder,xmlfile),
                         output_dir, folder, xmlfile, args))
        except UnicodeDecodeError:
            traceback.print_exc(file=sys.stdout)
            continue
    return files

def loop(args):
    if args.folder:
        files = loop_folder(args.folder, args, data_dir=args.data, output_dir=args.output)
    else:
        files = []
        for folder in os.listdir(args.data):
            files += loop_folder(folder, args, data_dir=args.data, output_dir=args.output)

    if args.multi > 1:
        from multiprocessing import Pool
        pool = Pool(args.multi)
        pool.map(process_file, files)
    else:
        map(process_file, files)

