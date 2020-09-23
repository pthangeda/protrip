PROTRIP - Probabilistic Risk-Aware Optimal Transit Planner
==========================================================
PROTRIP is a multiobjective optimal routing algorithm for transit networks. This repository hosts a proof-of-concept implementation of a multiobjective optimal routing planning algorithm and is under active development. Raise an issue if you notice any error or contact the authors [Pranay Thangeda](mailto:pranayt2@illinois.edu) and [Melkior Ornik](mailto:mornik@illinois.edu).

## Requirements
The conda environment with all the required packages is available in the env.yml file. The environment can be setup by using the following syntax:

```
conda env create -f env.yml
```

A docker container will be available at a further point in the development of the application. 

## Inputs
PROTRIP relies on GTFS feeds and accurate travel time data between stops to build the probablistic model of travel times in any transit network. In this implementation, we use the Champaign-Urbana Mass Transit District (CUMTD) GTFS feed [available here](https://developer.cumtd.com/). You can find GTFS static feeds of many major transit providers around the world at [this website](https://transitfeeds.com/). We use the historical schedule adherence records generated from the CAD/AVL system of CUMTD to extract the travel time data points at different road segments in the graph. The following image shows a preview of the stops and travel time data extracted from the GTFS feed and schedule adherence data extracted from CUMTD AVL.

<p align="center">
  <img src="https://github.com/pthangeda/protrip/blob/master/files/map_extractedata.PNG" width="400" title="Visualization of Extracted Data">
</p>

## Acknowledgment
Thanks to CUMTD for providing the data and insights of their operations. 

## Disclaimer
Please note that this is a proof-of-concept implementation as is a work-in-progress. The material embodied in this software is provided to you "as-is" and without warranty of any kind, express, implied or otherwise, including without limitation, any warranty of fitness for a particular purpose. In no event shall the authors and the organization they represent shall be liable to you or anyone else for any direct, special, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including without limitation, loss of profit, loss of use, savings or revenue, or the claims of third parties, whether or not the authors or their organization has been advised of the possibility of such loss, however caused and on any theory of liability, arising out of or in connection with the possession, use or performance of this software.
