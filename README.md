# 2D Wave Simulator on CPU

## Overview
This project simulates the 2D wave equation using Python, showcasing the propagation of waves through a medium. The simulation is visualized in real-time with PyQt and pyqtgraph, offering an interactive experience to understand wave dynamics. Big thanks to [2D Wave Simulation on the GPU](https://github.com/0x23/WaveSimulator2D) whose code is re-factored here.

<div style="display: flex;">
    <img src="screenshot.png" alt="Screenshot" width="100%">
</div>

## Features
- Real-time 2D wave propagation simulation.
- Customizable parameters for wave generation and medium properties.
- Interactive visualization using PyQt and pyqtgraph.

## Requirements
- Python 3.x
- PyQt5
- pyqtgraph
- numpy
- scipy

## Installation
To run the 2D Wave Simulator, you need to install the required Python libraries. Clone this repository and install the dependencies:

```bash
git clone git@github.com:mrmartin/wavesim.git
cd wavesim
pip install -r requirements.txt
```

## Usage
After installing the dependencies, run the simulation:

```bash
python3 animate_wave.py
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
