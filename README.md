# nodeScale
Scale area/power/energy/delay between VLSI nodes.

## Usage

Run the following to get the usage information:

```
python nodeScale.py -h
```

Notes:
- For sub-65nm nodes, HP/LP distinction is neccessary except for area. Area conversion accepts node names with and without "HP"/"LP".
- Except area, source and destination supply voltage needs to be provided. Please refer to the original paper (see below) for restrictions on VDD ranges.

## Excel Module

nodeScale.xlam provides MS Excel functions that perform the conversion. To use it, in Excel, go to Tools->Excel Add-Ins, select Browse and find the nodeScale.xlam file. It will make the follwing functions available:

```
AREASCALE(value, src, dst)
DELAYSCALE(value, src, dst, srcvdd, dstvdd)
ENERGYSCALE(value, src, dst, srcvdd, dstvdd)
POWERSCALE(value, src, dst, srcvdd, dstvdd)
```

## Scaling Equations

Scaling equations are based on the following (not mine) paper, if you use this script you should cite the original publication:

```
@article{stillmaker2017scaling,
  title={Scaling equations for the accurate prediction of CMOS device performance from 180 nm to 7 nm},
  author={Stillmaker, Aaron and Baas, Bevan},
  journal={Integration},
  volume={58},
  pages={74--81},
  year={2017},
  publisher={Elsevier}
}
```
