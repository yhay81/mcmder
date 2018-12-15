# mcmder
Yet Another Wrapper of Nysol M-Command in Python.


## Description

High-speed processing (CSV) of large-scale structured data tables.

To know more about Nysol and M-Command, see the official documents.


### What is Nysol and M-Command?
[Nysol Official Page](http://www.nysol.jp/en/home)

[M-Command GitHub](https://github.com/nysol/mcmd)


### How fast Nysol is?
[Nysol Biz Page (Japanese)](http://www.nysol.biz/)


## Features
- Create M-Command easily in python with method chaining. 
- Execute M-Command without putting large data on memory.(csv to csv)
- Optionally use pandas DataFrame as input and output.


## Requirement
- [nysol/mcmd](https://github.com/nysol/mcmd#installation)
- [pandas](https://pandas.pydata.org/)

## Install
```
pip install mcmder
```

## Usage

### From CSV File
sample.csv
```
a,b,c
x,1,4
y,2,9
z,3,3
```

```
>>> from mcmder import Mcmder
>>> m = Mcmder('sample.csv')
>>> mc = m.mcut(['a','c'])
>>> mc.save('cut.csv')
```

cut.csv
```
a,c
x,4
y,9
z,3
```

```
>>> mc.dataframe
   a  c
0  x  4
1  y  9
2  z  3
```

### From pandas DataFrame
```
>>> from mcmder import Mcmder
>>> import pandas as pd
>>> import numpy as np
>>> df = pd.DataFrame(np.random.randn(6,4), columns=list('ABCD'))
>>> m = Mcmder(df)
>>> mc = m.mcut(['A','C','D']).msel('${A}>0')
>>> mc.dataframe
          A         C         D
0  0.251857  0.080099 -1.211923
1  0.100167 -1.824585  0.051611
2  0.890079  1.440997 -0.298709
```

## License

[MIT](https://github.com/yhay81/mcmder/blob/master/LICENSE)


## Author

[Yusuke Hayashi](https://github.com/yahy81)
