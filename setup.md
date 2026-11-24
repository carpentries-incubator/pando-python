---
title: Setup
---

<!--
## Data Sets

FIXME: place any data you want learners to use in `episodes/data` and then use
       a relative link ( [data zip file](data/lesson-data.zip) ) to provide a
       link to it, replacing the example.com link.
       
Download the [data zip file](https://example.com/FIXME) and unzip it to your Desktop
-->

## Software Setup

::::::::::::::::::::::::::::::::::::::: discussion

### Details

This course was originally developed using Python 3.11 and last tested with Python 3.14. We recommend that you have a Python 3.14 environment.

You may want to create a new Python virtual environment for the course, this can be done with your preferred Python environment manager (e.g. `conda`, `pipenv`), the required packages can all be installed via `pip`.

If you have `conda` available, you can create and activate a new environment using the following command:

```sh
conda create --name prof_opt python=3.14
conda activate prof_opt
```

The non-core Python packages required by the course are `pytest`, `snakeviz`, `line_profiler`, `numpy`, `pandas` and `matplotlib` which can be installed via `pip`.
 
```sh
pip install pytest snakeviz "line_profiler[all]" numpy pandas matplotlib
```

To complete some of the exercises you will need to use a text-editor or Python IDE, so make sure you have your favourite available.

:::::::::::::: instructor

As the instructor, you should additionally install the `shapely` package, which you may need for a brief demo during the episode on scientific Python packages.

```sh
pip install shapely
```

:::::::::::::::::::::::::


:::::::::::::::::::::::::::::::::::::::::::::::::::

### Bonus Episode: Drop-in Replacements (optional)

The bonus episode on drop-in replacements for NumPy and Pandas needs some extra packages. Installing Modin currently downgrades Pandas, so please install these into a **separate** environment, rather than the main course environment:

```sh
conda create --name prof_opt_bonus python=3.14
conda activate prof_opt_bonus
pip install numpy scipy dpnp "modin[ray]"
```

If you are using an Intel Mac, or WSL on Windows, install `"modin[dask]"` instead of `"modin[ray]"`.

#### Intel GPU (DPNP)

DPNP runs NumPy code on Intel GPUs, including the integrated graphics in most recent Intel laptops. It is only available for Linux and Windows. If you have a Mac, or a computer without Intel graphics, you can still follow the episode using the outputs provided.

- **Windows**: the standard Intel graphics driver is usually already installed. If not, install the latest driver from [Intel's website](https://www.intel.com/content/www/us/en/download-center/home.html).
- **Linux**: you need Intel's GPU compute driver. On Ubuntu 24.04 (and derivatives such as Linux Mint 22), the packages in the standard repositories are too old for DPNP, so install them from Intel's graphics PPA:

  ```sh
  sudo add-apt-repository -y ppa:kobuk-team/intel-graphics
  sudo apt update
  sudo apt install -y libze-intel-gpu1 libze1 intel-opencl-icd
  ```

  For other distributions, see [Intel's GPU driver installation guide](https://dgpu-docs.intel.com/).

To check that DPNP can see your GPU, run:

```sh
python -m dpctl --full-list
```

You should see at least one device with `gpu` in its "Filter string", e.g. `level_zero:gpu:0`. If nothing is listed, the GPU driver is missing or too old.

#### NVIDIA GPU (CuPy, optional)

If you have a dedicated NVIDIA graphics card, you can also try the CuPy examples. Check which CUDA version your driver supports with `nvidia-smi`, then install the matching package, e.g.:

```sh
pip install "cupy-cuda13x[ctk]"
```

#### AMD GPU (CuPy, optional, Linux only)

CuPy also has experimental support for AMD graphics cards on Linux. You will need [ROCm 7](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html) installed and a GPU on [ROCm's supported list](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html). Then install:

```sh
pip install cupy-rocm-7-0
```

#### NVIDIA GPU (cuDF, optional, Linux or WSL2 only)

cuDF runs Pandas code on NVIDIA graphics cards. It needs Linux (or WSL2 on Windows 11) and a GPU with compute capability 7.0 or newer, which includes most NVIDIA cards from the last few years. cuDF does not yet support Python 3.14, and it should not be mixed with Modin, so install it into its **own** environment. Check which CUDA version your driver supports with `nvidia-smi`, then install the matching package:

```sh
conda create --name prof_opt_cudf python=3.12
conda activate prof_opt_cudf
pip install cudf-cu13      # or cudf-cu12 for CUDA 12 drivers
```

See [NVIDIA's installation guide](https://docs.nvidia.com/datascience/install/) for other options.

#### AMD GPU (hipDF, optional, Linux only)

hipDF is AMD's version of cuDF. **It currently only supports AMD Instinct datacenter GPUs** (MI210, MI250, MI300X, MI325X and MI355X), so in practice you will only find it on HPC systems; consumer Radeon cards are not supported. It needs Linux (Ubuntu 22.04 or 24.04) and [ROCm 10](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html). Install it into its own environment, separate from cuDF:

```sh
conda create --name prof_opt_hipdf python=3.12
conda activate prof_opt_hipdf
pip install amd-hipdf==4.0.0 --extra-index-url=https://pypi.amd.com/rocm-10.0.0/simple
```

To use hipDF's Pandas accelerator mode (as in the episode) you must also enable XNACK before starting Python:

```sh
export HSA_XNACK=1
```

See [AMD's hipDF installation guide](https://rocm.docs.amd.com/projects/hipDF/en/latest/install/INSTALL.html) for the full list of requirements.
