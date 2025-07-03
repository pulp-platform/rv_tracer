[comment]: <> (Authors:  Umberto Laghi, Samuele Righi)
[comment]: <> (Contact: umberto.laghi2@unibo.it, samuele.righi@studio.unibo.it)

# RISC-V Efficient Trace compliant Trace Decoder
[![Apache-2.0 license](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

Trace Decoder is developed as part of the PULP project, a joint effort between ETH Zurich and the University of Bologna.

## License
Unless specified otherwise in the respective file headers, all code checked into this repository is made available under a permissive license. All software sources and tool scripts are licensed under the Apache License 2.0 (see [`LICENSE`](LICENSE)) or compatible licenses, except for files contained in the `docs` directory, which are licensed under the [Creative Commons Attribution-NoDerivates 4.0 International](https://creativecommons.org/licenses/by-nd/4.0) license (CC BY-ND 4.0).

## How to run it
Download the repo and move inside it with command:
```
cd decoder
```

Download the dependencies using `pip`:
>[!IMPORTANT]
> It's raccomended the use of a virtual environment

```
pip install -r requirements
```

Run a test of your choice from the `test` directory:
```
python3 main.py ./tests/hello_culsans/packets.bin ./tests/hello_culsans/hello_culsans.riscv
```
The binary and the compiled files must belong to the same folder.