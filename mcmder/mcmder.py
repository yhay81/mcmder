"""Use M-Command from python."""
import os
import io
import copy
import subprocess
import pandas

from .errors import McmderError, McmdError
from .utils import df2bytes, clean_dic


class Mcmder(object):
    """Create/Contain M-Command and contain the result as pandas.DataFrame."""

    def __init__(self, input_data=None, header=True, *, _mcmd_args=None):
        """Check if input data is file path or pandas.df.

        :param str or pandas.DataFrame input_data:
        :param list _mcmd_args:
        """
        if not(input_data is None or isinstance(input_data, str) or
               isinstance(input_data, pandas.DataFrame)):
            raise ValueError(
                'Input data must be str(file path) or pandas.DataFrame.')
        elif isinstance(input_data, str) and not os.path.exists(input_data):
            raise ValueError('Input file does not exist.')
        self.input_data = input_data
        self._mcmd_args = _mcmd_args
        self.header = header
        self._dataframe = None

    @property
    def statement(self):
        return ' '.join(self._mcmd_args) if self._mcmd_args else None

    def save(self, output_file, create_dataframe=False):
        """Save data as a csv.

        :param str output_file: file path to write
        :param bool create_dataframe: save also as a dataframe
        """
        if self._dataframe is not None:
            self._dataframe.to_csv(output_file)
        elif create_dataframe:
            self._dataframe = pandas.read_csv(
                io.BytesIO(self.execute(output_file, stdout=True)))
        else:
            self.execute(output_file)
        return self

    @property
    def dataframe(self):
        if self._dataframe is None:
            self._dataframe = pandas.read_csv(
                io.BytesIO(self.execute(stdout=True)))
        return self._dataframe

    df = dataframe

    def execute(self, output_file=None, stdout=False, header=False):
        """Execute M-Command.

        if output_file is not None, just write into the file.
        :param str output_file: file path to write
        :param bool stdout: get bytes stdout
        :rtype: bytes
        """
        if self._mcmd_args is None:
            raise McmderError("This mcmder does not have commands yet.")
        args = copy.copy(self._mcmd_args)
        if output_file is not None and stdout:
            args.append('|mtree o=' + output_file)
        elif output_file is not None and not stdout:
            args.append('o=' + output_file)
        if header:
            args.append('-nfno')
        stdin = df2bytes(self.input_data) \
            if isinstance(self.input_data, pandas.DataFrame) else None
        completed_process = subprocess.run(
            ' '.join(args), input=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        if completed_process.returncode != 0:
            raise McmdError(
                completed_process.returncode, ' '.join(args),
                output=completed_process.stdout,
                stderr=completed_process.stderr
            )
        return completed_process.stdout

    def mcmd(self, mcmd_name, *flags, **options):
        """Return new Mcmder added new command.

        flags are added as '-flag', options are added as 'key=value'
        into M-Command
        :param str mcmd_name: M-Command name like 'mcut'
        :rtype: Mcmder
        """
        matched_set = set(flags) & {'params', 'help', 'helpl', 'version'}
        if matched_set != set():
            for flag in matched_set:
                completed_process = subprocess.run(
                    [mcmd_name, '-' + flag], stdout=subprocess.PIPE)
                print(completed_process.stdout)
            return self
        if self._mcmd_args is None:
            if isinstance(self.input_data, str):
                next_args = [mcmd_name, 'i=' + self.input_data]
            else:
                next_args = [mcmd_name, ]
            if not self.header:
                next_args.append('-nfn')
        else:
            next_args = copy.copy(self._mcmd_args)
            next_args.append('|')
            next_args.append(mcmd_name)
        for flag in flags:
            if flag is not None:
                next_args.append('-' + flag)
        for key, value in options.items():
            if value is not None:
                next_args.append(key + '=' + value)
        return Mcmder(self.input_data, True, _mcmd_args=next_args)

    # Each Commands
    def maccum(self, f, s, k=None, *options, tmpPath=None, precision=None):
        return self.mcmd('maccum', *options, **clean_dic(locals()))

    def marff2csv(self, *options, tmpPath=None):
        return self.mcmd('marff2csv', *options, **clean_dic(locals()))

    def mavg(self, f, k, *options, tmpPath=None, precision=None):
        return self.mcmd('mavg', *options, **clean_dic(locals()))

    def mbest(self, s, from_=0, to=0, k=None, u=None, *options, tmpPath=None):
        return self.mcmd('mbest', *options, **clean_dic(locals()))

    def mbucket(self, f, n, F=0, k=None, O=None,
                *options, bufcount=None, tmpPath=None, precision=None):
        return self.mcmd('mbucket', *options, **clean_dic(locals()))

    def mcat(self, f, *options, tmpPath=None):
        return self.mcmd('mcat', *options, **clean_dic(locals()))

    def mchgnum(self, f, R, v, O=None, *options, tmpPath=None):
        return self.mcmd('mchgnum', *options, **clean_dic(locals()))

    def mchgstr(self, c, f, O=None, *options, tmpPath=None):
        return self.mcmd('mchgstr', *options, **clean_dic(locals()))

    def mchkcsv(self, a, f, n, s=None, k=None, *options, tmpPath=None):
        return self.mcmd('mchkcsv', *options, **clean_dic(locals()))

    def mcombi(self, a, f, n, s=None, k=None, *options, tmpPath=None):
        return self.mcmd('mcombi', *options, **clean_dic(locals()))

    def mcommon(self, k, K=None, u=None, m=None, *options, tmpPath=None):
        return self.mcmd('mcommon', *options, **clean_dic(locals()))

    def mcount(self, a, k=None, *options, tmpPath=None):
        return self.mcmd('mcount', *options, **clean_dic(locals()))

    def mcross(self, f, s, a=None, k=None, v=None, *options, tmpPath=None):
        return self.mcmd('mcross', *options, **clean_dic(locals()))

    def m2cross(self, f, s=None, a=None, k=None, v=None,
                *options, tmpPath=None):
        return self.mcmd('m2cross', *options, **clean_dic(locals()))

    def mcsv2json(self, k=None, s=None, f=None, h=None, p=None,
                  *options, tmpPath=None):
        return self.mcmd('mcsv2json', *options, **clean_dic(locals()))

    def mcsvconv(self, m, k=None, s=None, *options, tmpPath=None):
        return self.mcmd('mcsvconv', *options, **clean_dic(locals()))

    def mcut(self, f, *options, tmpPath=None):
        return self.mcmd('mcut', *options, **clean_dic(locals()))

    def mdata(self, O=None, *options):
        return self.mcmd('mdata', *options, **clean_dic(locals()))

    def mdelnull(self, f, k=None, u=None, *options, tmpPath=None):
        return self.mcmd('mdelnull', *options, **clean_dic(locals()))

    def mdformat(self, c, f, *options, tmpPath=None):
        return self.mcmd('mdformat', *options, **clean_dic(locals()))

    def mdsp(self, x, y, str=None, fc=None, bg=None, *options):
        return self.mcmd('mdsp', *options, **clean_dic(locals()))

    def mduprec(self, f=None, n=None, *options, tmpPath=None):
        return self.mcmd('mduprec', *options, **clean_dic(locals()))

    def mfldname(self, f=None, n=None, tmpPath=None):
        return self.mcmd('mfldname', *options, **clean_dic(locals()))

    def mfsort(self, f, *options, tmpPath=None):
        return self.mcmd('mfsort', *options, **clean_dic(locals()))

    def mhashavg(self, f, hs=None, k=None,
                 *options, tmpPath=None, precison=None):
        return self.mcmd('mhashavg', *options, **clean_dic(locals()))

    def mhashsum(self, f, hs=None, k=None, *options,
                 tmpPath=None, precision=None):
        return self.mcmd('mhashsum', *options, **clean_dic(locals()))

    def minput(self, x, y, len, f=None, *options):
        return self.mcmd('minput', *options, **clean_dic(locals()))

    def mjoin(self, k, f=None, K=None, m=None, *options, tmpPath=None):
        return self.mcmd('mjoin', *options, **clean_dic(locals()))

    def mkeybreak(self, k, s=None, a=None, *options, tmpPath=None):
        return self.mcmd('mkeybreak', *options, **clean_dic(locals()))

    def mmbucket(self, f, n, F=None, k=None, O=None, *options,
                 bufcount=None, tmpPath=None):
        return self.mcmd('mmbucket', *options, **clean_dic(locals()))

    def mminput(self, f=None, *options, tmpPath=None):
        return self.mcmd('mminput', *options, **clean_dic(locals()))

    def mmseldsp(self, x, y, height=None, seldata=None, *options):
        return self.mcmd('mmseldsp', *options, **clean_dic(locals()))

    def mmvavg(self, f, s=None, k=None, n=None, t=None, alpha=None, skip=None,
               *options, tmpPath=None, precision=None):
        return self.mcmd('mmvavg', *options, **clean_dic(locals()))

    def mmvsim(self, f, c, a, s=None, k=None, t=None, skip=None,
               *options, tmpPath=None, precision=None):
        return self.mcmd('mmvsim', *options, **clean_dic(locals()))

    def mmvstats(self, f, c, s=None, k=None, t=None, skip=None,
                 *options, tmpPath=None, precision=None):
        return self.mcmd('mmvstats', *options, **clean_dic(locals()))

    def mnewnumber(self, a, I=None, S=None, l=None, *options, tmpPath=None):
        return self.mcmd('mnewnumber', *options, **clean_dic(locals()))

    def mnewrand(self, a, max=None, min=None, S=None, l=None,
                 *options, tmpPath=None):
        return self.mcmd('mnewrand', *options, **clean_dic(locals()))

    def mnewstr(self, a, v=None, l=None, *options, tmpPath=None):
        return self.mcmd('mnewstr', *options, **clean_dic(locals()))

    def mnjoin(self, k, f=None, K=None, m=None,
               *options, bufcount=None, tmpPath=None):
        return self.mcmd('mnjoin', *options, **clean_dic(locals()))

    def mnormalize(self, c, f, k=None,
                   *options, bufcount=None, tmpPath=None, precision=None):
        return self.mcmd('mnormalize', *options, **clean_dic(locals()))

    def mnrcommon(self, R, r, k=None, K=None, u=None, m=None,
                  *options, tmpPath=None):
        return self.mcmd('mnrcommon', *options, **clean_dic(locals()))

    def mnrjoin(self, R, r, k=None, K=None, f=None, *options, tmpPath=None):
        return self.mcmd('mnrjoin', *options, **clean_dic(locals()))

    def mnullto(self, f, v=None, O=None, *options, tmpPath=None):
        return self.mcmd('mnullto', *options, **clean_dic(locals()))

    def mnumber(self, a, e=None, I=None, k=None, s=None, S=None,
                *options, tmpPath=None):
        return self.mcmd('mnumber', *options, **clean_dic(locals()))

    def mpadding(self, f, k=None, v=None, S=None, E=None,
                 *options, tmpPath=None):
        return self.mcmd('mpadding', *options, **clean_dic(locals()))

    def mpaste(self, f, m=None, *options, tmpPath=None):
        return self.mcmd('mpaste', *options, **clean_dic(locals()))

    def mproduct(self, f, m=None, *options, bufcount=None, tmpPath=None):
        return self.mcmd('mproduct', *options, **clean_dic(locals()))

    def mrand(self, a, k=None, max=None, min=None, S=None,
              *options, tmpPath=None):
        return self.mcmd('mrand', *options, **clean_dic(locals()))

    def mrjoin(self, r, k=None, K=None, R=None, f=None, m=None,
               *options, tmpPath=None):
        return self.mcmd('mrjoin', *options, **clean_dic(locals()))

    def msed(self, c, f, v, *options, tmpPath=None):
        return self.mcmd('msed', *options, **clean_dic(locals()))

    def msel(self, c, u=None, *options, tmpPath=None):
        return self.mcmd('msel', *options, **clean_dic(locals()))

    def mseldsp(self, x, y, height=None, seldata=None, *options):
        return self.mcmd('mseldsp', *options, **clean_dic(locals()))

    def mselnum(self, f, c, k=None, u=None,
                *options, bufcount=None, tmpPath=None):
        return self.mcmd('mcut', *options, **clean_dic(locals()))

    def mselrand(self, c=None, p=None, k=None, S=None, *options, tmpPath=None):
        return self.mcmd('mselrand', *options, **clean_dic(locals()))

    def mselstr(self, f, v, k=None, u=None,
                *options, bufcount=None, tmpPath=None):
        return self.mcmd('mselstr', *options, **clean_dic(locals()))

    def msep(self, d, f=None, *options, tmpPath=None):
        return self.mcmd('msep', *options, **clean_dic(locals()))

    def msep2(self, k, O, a, *options, tmpPath=None):
        return self.mcmd('msep2', *options, **clean_dic(locals()))

    def msetstr(self, v, a, *options, tmpPath=None):
        return self.mcmd('msetstr', *options, **clean_dic(locals()))

    def mshare(self, f, k=None, *options, tmpPath=None):
        return self.mcmd('mshare', *options, **clean_dic(locals()))

    def mshuffle(self, d, n=None, v=None, f=None, *options, tmpPath=None):
        return self.mcmd('mshuffle', *options, **clean_dic(locals()))

    def msim(self, c, f, a=None, k=None, n=None,
             *options, bufcount=None, tmpPath=None, precision=None):
        return self.mcmd('msim', *options, **clean_dic(locals()))

    def mslide(self, f, s=None, k=None, t=None, *options, tmpPath=None):
        return self.mcmd('mslide', *options, **clean_dic(locals()))

    def msortf(self, f, pways=None, maxlines=None, blocks=None, threadCnt=None,
               *options, tmpPath=None):
        return self.mcmd('msortf', *options, **clean_dic(locals()))

    def msplit(self, f, a, delim=None, *options, tmpPath=None):
        return self.mcmd('msplit', *options, **clean_dic(locals()))

    def mstats(self, c, f, k=None, *options, tmpPath=None, precision=None):
        return self.mcmd('mstats', *options, **clean_dic(locals()))

    def msum(self, f, k=None, *options, tmpPath=None, precision=None):
        return self.mcmd('msum', *options, **clean_dic(locals()))

    def msummary(self, c, f, a=None, k=None,
                 *options, tmpPath=None, precision=None):
        return self.mcmd('msummary', *options, **clean_dic(locals()))

    def mtee(self, *options, tmpPath=None):
        return self.mcmd('mtee', *options, **clean_dic(locals()))

    def mtonull(self, f, v, *options, tmpPath=None):
        return self.mcmd('mtonull', *options, **clean_dic(locals()))

    def mtra(self, f, s=None, k=None, delim=None, *options, tmpPath=None):
        return self.mcmd('mtra', *options, **clean_dic(locals()))

    def mtrafld(self, a, f=None, delim=None, delim2=None,
                *options, tmpPath=None):
        return self.mcmd('mtrafld', *options, **clean_dic(locals()))

    def mtraflg(self, a, f, delim=None, *options, tmpPath=None):
        return self.mcmd('mtraflg', *options, **clean_dic(locals()))

    def muniq(self, k, *options, tmpPath=None):
        return self.mcmd('muniq', *options, **clean_dic(locals()))

    def mvcommon(self, vf, K=None, m=None, delim=None, *options, tmpPath=None):
        return self.mcmd('mvcommon', *options, **clean_dic(locals()))

    def mvcount(self, vf, delim=None, *options, tmpPath=None):
        return self.mcmd('mvcount', *options, **clean_dic(locals()))

    def mvdelim(self, vf, v, delim=None, *options, tmpPath=None):
        return self.mcmd('mvdelim', *options, **clean_dic(locals()))

    def mvdelnull(self, vf, delim=None, *options, tmpPath=None):
        return self.mcmd('mvdelnull', *options, **clean_dic(locals()))

    def mvjoin(self, vf, K, f, n=None, m=None, delim=None, *options, tmpPath=None):
        return self.mcmd('mvjoin', *options, **clean_dic(locals()))

    def mvnullto(self, vf, v=None, O=None, *options, tmpPath=None):
        return self.mcmd('mvnullto', *options, **clean_dic(locals()))

    def mvreplace(self, vf, K, f, n=None, m=None, delim=None, *options, tmpPath=None):
        return self.mcmd('mvreplace', *options, **clean_dic(locals()))

    def mvsort(self, vf, delim=None, *options, tmpPath=None):
        return self.mcmd('mvsort', *options, **clean_dic(locals()))

    def mvuniq(self, vf, delim=None, *options, tmpPath=None):
        return self.mcmd('mvuniq', *options, **clean_dic(locals()))

    def mwindow(self, wk, t, k=None, *options, tmpPath=None):
        return self.mcmd('mwindow', *options, **clean_dic(locals()))

    def mxml2csv(self, k, f, *options, tmpPath=None):
        return self.mcmd('mxml2csv', *options, **clean_dic(locals()))

    def mcal(self, a, c, *options, tmpPath=None, precision=None):
        return self.mcmd('mcal', *options, **clean_dic(locals()))
