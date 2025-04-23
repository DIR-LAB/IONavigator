# Silicon Photonics I/O Nodes for HPC Applications

Luca Ramini, Yanir London, Daniel Dauwe, Jared Hulme,

Steven Dean, Marco Fiorentino, and Raymond G. Beausoleil

*Abstract*—We propose a silicon photonics (SiPh) node that is tightly-coupled to the compute node and uses an integrated photonic crossbar to implement optical pass-through links for building an all-to-all, always on, large scale, low latency, and switchless optical network for high performance computing.

*Index Terms*—Silicon photonics, high performance computing.

I. INTRODUCTION

The rapid increase in large-scale machine learning, artificial intelligence, and data analytics applications accelerate the adaptation of HPC systems [1]. HPC systems are capable of processing large-scale data and performing very complex calculations at high speeds due to a pod design that consists of close-knitted nodes linked by a high-performance interconnect fabric. This fabric typically consists of a switchbased network [2]. However, as traffic demand of modern applications increases, high intra-node latency is accumulated in the switches' buffers causing congestion. An all-to-all (A2A) connected compute nodes topology (with a direct path between any two nodes) is the most favorable solution for this issue, because it provides the lowest intra-node latency, thus enabling a switchless network. Currently available electrical A2A networks for HPC are brute force designs with a direct connection for each nodes pair, which become expensive in large-scale systems (e.g., 256 nodes) due to the quadratic growth of the number of connections with network compute nodes. Also, electrical links cannot achieve the data rates needed in modern systems due to their limited bandwidth and high crosstalk [3], [4]. Replacing electrical interconnects with optical counterpart can resolve the bandwidth issue, but A2A optical networks, based on pluggable optical transceivers, are still expensive because implemented through a brute force approach. We address this problem by proposing a SiPh I/O node which is tightly coupled to a compute node and uses an integrated photonic crossbar to realize optical pass-through (OPT) links, thus enabling an A2A, always on, scalable, and switchless optical network with predictable latency for HPC.

## II. A2A SWITCHLESS NETWORK VIA SIPH I/O NODES

An A2A switchless optical network which makes use of our SiPh I/O nodes is shown in figure 1. It consists of M groups of N nodes per group that are locally-connected, while each of the nodes in the m-th group is globally-connected to each of the nodes in the other groups. The global connection is either direct- or OPT-link. Figure 1 specifically shows a 9-node network configured into 3 groups and 3 nodes per group, where the nodes [m,n] (m=1,2,3 and n=1,2,3) belong to the m-th group. We define the pair [m2,n] and [m3,n] as

![](_page_0_Figure_11.png)

Fig. 1. A2A switchless optical network fabric with 9 compute nodes.

![](_page_0_Figure_13.png)

Fig. 2. Example of an optical pass-through link used for a diagonal connection between node [1,2] and node [2,3]. Node [1,2] sends 8 wavelength channels (λo) to node [2,3] passing through a photonic crossbar (PXbar) in node [2,2] and reusing direct fibers. The rectangles (right side) indicate SiPh I/O nodes including grating couplers, waveguides, ring modulators/filters, and PXbar.

the global twin nodes of the node [m1,n], where m1,m2,m3 [1,2,3] and m1 6= m2 6= m3. Network scalability can be achieved by increasing M groups, N nodes per group, or both, while bandwidth scalability can be obtained by aggregating many wavelengths over the optical link. A2A connectivity between nodes is achieved by defining a color group (λ-group), which consists of multiple wavelengths for Local, Global, and OPT links. We specified the routing of data assuming three wavelength groups: λb is used for Local- and Globaldirect links while λg and λo are used for OPT links. Unlike brute force A2A networks, our A2A concept leverages OPT links that run concurrently, i.e., always on, where no fiber is required to directly connect between all four diagonal nodes (e.g. between nodes [1,1] and [2,2]). This effect becomes even more important by increasing the node count where the majority of connections will be diagonal links. Thus, our A2A concept enables to reduce the amount of fibers and connectors.

## III. DIRECT AND OPT LINKS FOR SIPH I/O NODES

An example of direct link is shown in figure 1. Node [1,2] is directly connected to its local neighbors [1,1] and [1,3] using

This work has been done during the employment of the authors at Hewlett Packard Enterprise. Luca Ramini, Yanir London, Jared Hulme, Marco Fiorentino, and Raymond G. Beausoleil are with Hewlett Packard Labs, Hewlett Packard Enterprise, Milpitas, USA. Steven Dean is with Hewlett Packard Enterprise, Chippewa Falls, USA. Daniel Dauwe is with Google, USA. Corresponding author: Luca Ramini, email: luca.ramini@hpe.com.

![](_page_1_Figure_1.png)

Fig. 3. SiPh I/O node: 160 ring resonators in total, 64 ring modulators and 64 ring filters in local/global TXs/RXs, plus 32 ring filters in PXbar.

![](_page_1_Figure_3.png)

Fig. 4. Rx eye diagram at 16 Gbps for an optical pass-through link.

λb over two different bidirectional fibers (see blue dashed arrows). Node [1,2] also uses λb to directly communicate with its global twins [2,2] and [3,2] (nodes of global group 2 and 3 respectively) over two different bidirectional fibers (see blue arrows), thus establishing two independent global direct links. An OPT link is used for a diagonal unidirectional communication. For example, [1,2] sends data to [2,1] and [2,3] via its global twin node [2,2] using λg and λo respectively (see green and orange arrows in figure 1). The global twin node [2,2] acts as a pass-through node as it allows to transparently pass the data to the diagonal node ([2,1] or [2,3]) using a photonic crossbar (PXbar), with no need for any additional diagonal direct fiber. An OPT link is also detailed in figure 2. We designed SiPh I/O node including a photonic IC (PIC), an electronic IC (EIC), an FPGA host, and network and link-level simulation models for a 9-node A2A fabric. The left side of figure 3 shows the compute node directly coupled to our SiPh I/O node chip. The right side shows the layout of the SiPh I/O node and its micro-architecture with five distinctive parts: Local and Global transmitters, Local and Global receivers, and PXbar. SiPh devices such as waveguides, grating couplers, micro-ring modulators (filters) are used within transmitters (receivers). PXbar has 4 arrays of 8 ring filters each and acts as a wavelength-routed optical router to implement OPT links.

## IV. EVIDENCE THE SOLUTION WORKS

With our OPT concept implemented through PXbar we innovated by significantly reducing the fiber count compared to a brute force approach. For a 9-node network, by eliminating diagonal links, the total number of fiber pairs per node reduces from 8 to 4. This saving increases for large-scale networks: the number of fiber pairs per node reduces from 127 to 22 (80% saving) for a 128-node system configured into 8 groups

![](_page_1_Figure_8.png)

Fig. 5. Injection load vs. mean latency for different traffic patterns: load (percentage of theoretical total node bandwidth) on the x-axis and mean latency achieved at each load for three traffic patterns on the y-axis.

and 16 nodes per group. This enables a significantly lower cost A2A network and makes our SiPh I/O node a viable solution for HPC. We estimated SiPh I/O node power based on electronic chip results with 28-nm CMOS technology [5] and silicon photonics PDK. It consumes about 15.5 W for a 9 node network while increasing to about 40 W for a 128-node network. We see x2.5 power increase w.r.t x14 increase in node count. The photonic static power is only a small portion of the total node power, about 3 % for a compute node of 500 W, in the case of a 9-node example. We also performed time domain simulations using Lumerical INTERCONNECT [6] and devices of our SiPh PDK to analyze bit error rate (BER) performance for direct and OPT links at 16 Gbps. Figure 4 shows the eye diagram of one of the received signals for an OPT link at 16 Gbps. We see no significant degradation of eye opening and the estimated BER is ≤ 1E-12 across all channels. Figure 5 shows the performance of three traffic patterns (uniform random, random exchange, A2A broadcast) with load vs. mean latency achieved. While our switchless network still experiences increased latency with the random exchange traffic (as a traditional network also would) its A2A network allows broadcast traffic to perform well with very little increase in latency as more demand is placed on it.

## V. CONCLUSION

We proposed SiPh I/O node for a scalable, always on, A2A switchless network. To the best of our knowledge our idea is the first of its kind that enables an A2A fabric that scales to hundreds and potentially thousands of nodes where latency properties are achieved via SiPh and CMOS IC-3D packaging technologies for best cost, design resources and efficiencies.

### REFERENCES

- [1] "High Performance Computing (HPC) Market by Component Solutions Servers, Storage, Networking Devices, and Software and Services, Deployment Type, Organization Size, Server Prices Band, Application Area, and Region - Global Forecast to 2025".
- [2] J.H. Ahn, N. Binkert, A. Davis, M. McLaren, and R.S. Schreiber, "HyperX: Topology, Routing, and Packaging of Efficient Large-Scale Networks," Proceedings of the Conference on High Performance Computing Networking, Storage and Analysis, pp. 1–11, 2009.
- [3] D. A. B. Miller, "Rationale and challenges for optical interconnects to electronic chips," Proceedings of the IEEE, pp. 728–749, 2000.
- [4] P. Fotouhi, S. Werner, and S. J. Ben Yoo, "Enabling Scalable Chipletbased Uniform Memory Architectures with Silicon Photonics," Proceed-
- ings of the Int. Symposium on Memory Systems, pp. 222–234, 2019. [5] J. Youn et al.,"3D-Integrated DWDM Silicon Photonics Receiver," Integrated Photonics Research, Silicon & Nanophotonics,"ITu4A.4, 2021.
- [6] Photonic Circuit Simulator, www.lumerical.com/products/interconnect/.

