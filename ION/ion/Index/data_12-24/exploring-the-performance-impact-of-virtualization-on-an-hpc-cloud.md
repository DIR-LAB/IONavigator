# Exploring the Performance Impact of Virtualization on an HPC Cloud

Nuttapong Chakthranont, Phonlawat Khunphet Department of Electrical and Computer Engineering King Mongkut's University of Technology North Bangkok 1518 Pracharat 1 Road, Bangsue, Bangkok, 10800, Thailand Email: {Nuttapong.chak, Khunphet.p}@gmail.com

*Abstract*—The feasibility of the cloud computing paradigm is examined from the High Performance Computing (HPC) viewpoint. The impact of virtualization is evaluated on our latest private cloud, the AIST Super Green Cloud, which provides elastic virtual clusters interconnected by InfiniBand. Performance is measured by using typical HPC benchmark programs, both on physical and virtual cluster computing clusters. The results of the micro benchmarks indicate that the virtual clusters suffer from the scalability issue on almost all MPI collective functions. The relative performance gradually becomes worse as the number of nodes increases. On the other hand, the benchmarks based on actual applications, including LINPACK, OpenMX, and Graph 500, show that the virtualization overhead is about 5% even when the number of nodes increase to 128. This observation leads to our optimistic conclusions on the feasibility of the HPC Cloud.

## I. INTRODUCTION

The cloud computing paradigm is known to have various advantages, such as the ability to provide a customized software environment for each user, elasticity due to its ability to scale in and scale out, and energy efficiency. These advantages also benefit the sharing of proprietary computer resources within an organization. We are thus building a private cloud platform on our recently introduced supercomputer system, the AIST Super Green Cloud, intended to provide a system for High Performance Computing (HPC) users. Such an HPC platform on the cloud is called an *HPC Cloud*. In terms of HPC, however, the most demanding issue is the overhead due to resource virtualization for cloud computing. We have observed that the virtualization penalty on the raw FLOPS count is negligible, though the communication performance is severely degraded when we employed virtualized interfaces. To encourage users to migrate from a traditional HPC platform to our HPC Cloud, we have to improve the communication performance by exploiting Virtual Machine Monitor (VMM) bypass I/O technologies, including PCI passthrough and SR-IOV.

We have employ the Apache CloudStack [1] as the foundation upon which to construct our HPC Cloud. The Apache CloudStack is a popular open source cloud infrastructure software suite, equipped with a comprehensive set of features to orchestrate virtual machines (VMs), networks, and storage. To adapt the Apache CloudStack for our HPC Cloud, we have integrated VMM-bypass I/O technologies into the CloudStack [2]. This extended version of the CloudStack provides virtual

Ryousei Takano, Tsutomu Ikegami Information Technology Research Institute, National Institute of Advanced Industrial Science and Technology Tsukuba, Ibaraki 305-8568, Japan Email: {takano-ryousei, t-ikegami}@aist.go.jp

clusters interconnected by the InfiniBand network fabric for users. A *virtual cluster* is a set of VMs that are built on top of a physical cluster, leveraging virtualization technologies. We assume a Beowulf-type virtual cluster that consists of two components: a front-end node and a set of compute nodes [3]. The front-end node is an entry point for users to submit jobs, which are then processed on the compute nodes.

In this paper, we quantitatively assess the performance impact of virtualization, comparing the performance of typical HPC programs between a physical cluster and a virtual cluster. To the best of our knowledge, evaluating the impact of virtualization on a large scale HPC Cloud platform has not yet been examined. Our contributions are described as follows. First, almost all MPI collective functions suffer from the scalability issue, though the point-to-point throughput is comparable to a physical cluster. The overhead of virtualization becomes significant as the number of nodes increases. On a 128-node virtual cluster, some benchmarks took twice as much execution time as the corresponding results on the physical cluster. Second, we got positive results for our HPC Cloud on benchmarks with real HPC applications. The virtualization overhead is, at most 5%, on a 128-node virtual cluster in which the number of CPU cores is 2560.

The rest of the paper is organized as follows. Section II briefly presents related work on I/O virtualization mechanisms and HPC Clouds. The experimental setting and the results are shown in Section III and Section IV, respectively. In Section V, we discuss new insights and open issues obtained from our experimental results. Finally, Section VI summarizes the paper.

## II. RELATED WORK

Virtualization is a key technology in cloud computing. It enables us to provide benefits of flexibility and resiliency for not only enterprise users but also HPC users. However, overhead caused by the virtualization is not negligible, especially in terms of I/O performance [4]. This is because I/O devices are emulated or para-virtualized on a virtual cluster. To cope with this performance problem, we can take advantage of VMMbypass I/O technologies, including PCI passthrough and Single Root I/O Virtualization (SR-IOV) [5]. PCI passthrough enables a guest OS to directly access physical PCI devices. Although PCI passthrough can achieve a nearly-native performance

978-1-4799-4093-6/14 $31.00 © 2014 IEEE DOI 10.1109/CloudCom.2014.71

level, it does not allow sharing of the device with another guest OS. In contrast, SR-IOV allows multiple guest OSs to simultaneously access a single PCI device.

Previous works have demonstrated promising advantage of VMM-bypass I/O technologies in the HPC field [6]–[8]. They have concluded that PCI passthrough and/or SR-IOV achieve performance comparable to a physical machine in almost all experiments. For instance, Ruivo, et al. [7] have integrated SR-IOV with the FermiCloud. Similarly, we will examine the impact of virtualization on popular HPC benchmarks by using our practical HPC Cloud built on top of the Apache CloudStack. Although these previous studies show the performance comparisons on a small cluster environment, we have conducted experiments on both a 128-node physical cluster and the corresponding virtual cluster.

The implementation of a virtual cluster is categorized into three types: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and multi-cloud. Our HPC Cloud is a private IaaS cloud, and it provides users with their own virtual clusters on demand. From this vantage point, with respect to major competitors with our work, other studies have been proposed, such as the Elastic Cloud Computing Cluster (EC3) [9], Wrangler [10], and StarCluster [11]. EC3 is a tool that creates an elastic virtual cluster on top of an IaaS cloud which can dynamically scale in and scale out, depending on user requirements. Wrangler is capable of provisioning a virtual cluster on different cloud providers such as Amazon EC2, Eucalyptus, and OpenNebula. On the other hand, ViteraaS [12] supports a PaaS cloud for running HPC programs on a virtual cluster. Unlike IaaS clouds, it provides a job execution service, and users cannot access a cluster node directly. Multi-cloud is another model for federating multiple clouds, and it is useful for cloud bursting, disaster recovery, and so on. Elastic Site [13] dynamically and securely extends an existing physical cluster into a Nimbus-based cloud and the Amazon EC2. Furthermore, its successor system [14] allows VMs to dynamically join and leave a virtual cluster at runtime. Ruben, et al. [15] proposed a flexible and generic virtual cluster architecture over a local cluster and a cloud provider.

Many virtual cluster management tools and systems have been proposed as mentioned above. Although we have demonstrated the impact of virtualization on our HPC Cloud, our approach and results can be applicable to these other systems.

# III. EXPERIMENT

# *A. Experimental Setting*

The virtual cluster runs on a physical cluster. For the base physical cluster, we have used the AIST Super Green Cluster (ASGC), which is the latest supercomputer at AIST. Its theoretical peak performance is 69.44 TFLOPS. It composes of 155 nodes of Cray H2312 blade servers. Each node has two Intel Xeon E5-2680 v2 (Ivy Bridge EN) 2.8 GHz processors, 128 GB of memory (DDR3-1866), a 600 GB SSD, a Mellanox ConnectX-3 FDR InfiniBand HCA, and a 10 Gigabit Ethernet NIC. The Intel Xeon E5-2680 v2 supports the Intel-VT technology for hardware virtualization. All nodes are connected by a full bisection bandwidth InfiniBand network, in which Mellanox SX6025 FDR switches are used. The 10 Gigabit Ethernet network is also used for the console service, storage network, and so on. We disabled the Hyper Threading capability.

Our HPC Cloud platform is built based on the Apache CloudStack 4.3.0 and the QEMU/KVM hypervisor version 0.12.1.2. We have extended the CloudStack to allow users to construct virtual clusters with direct access to an InfiniBand HCA without intervention from the hypervisor. A virtual cluster consists of a set of VMs. In our experiments, only a single VM is running on the physical node. Each VM has 20 VCPU cores and 120 GB of memory, and all VMs are connected by an InfiniBand network. The following software settings are identical for both a physical cluster and virtual clusters. The Operating System installed is CentOS version 6.5. Each node has the Intel Compiler version SP1 1.1.106, the Intel Math Kernel Library version SP1 1.1.106, the Mellanox OpenFabrics Enterprise Distribution (MLNX OFED) version 2.1, and the Open MPI version 1.6.5 [16] installed. The firmware version of ConnectX-3 is 2.11.1308.

As a key point to the HPC performance, the *transparent huge pages* feature is enabled on both the host and the guest OSs, in which we can use 2 MB huge pages as well as 4 KB pages. By allocating huge pages for a guest OS, less memory is required for page tables and TLB misses are reduced, thereby increases performance. In addition, we set up VCPU pinning which statically binds a virtual CPU core to a physical CPU core. On a NUMA system like the latest x86-64 architecture, memory affinity is an important concern in enhancing the performance of HPC applications. It can be more effective if a process is pinned to a processor core in such a way that its memory allocations are always local to the processor socket it is running on. This avoids inter-socket memory transfer, which has less bandwidth and can significantly degrade performance. The details will be discussed in Section V.

# *B. Benchmark Programs*

To evaluate the impact of virtualization for HPC use cases, we have conducted performance comparisons between a physical cluster and a virtual cluster through a set of popular HPC benchmark programs, including traditional HPC workloads, nano-scale material simulations, and graph processing. We used a subset of the ASGC as a physical cluster. A virtual cluster was built on top of the ASGC as described above. On both clusters, the number of nodes varies from 1 to 128 nodes. We tested three times for each benchmark program and took the average value.

*1) Intel Micro Benchmark (IMB):* IMB is a Message Passing Interface (MPI) [17]-level micro-benchmark suite to measure the performance of fundamental MPI functions, including point-to-point and collective communications, for a range of message sizes. We used the IMB version 3.2.4. As shown in Table I, we focus on the following six functions, bcast, allgather, allreduce, alltoall, and barrier, which are used in application-level benchmark programs.

*2) HPC Challenge (HPCC):* HPCC [18] is a benchmark suite that consists of seven benchmark programs and measures the performance of the CPU, memory, and the interconnect. This paper focuses on four of the most challenging benchmark programs: Global High Performance Linpack (G-HPL), EP-STREAM Triad, Global RandomAccess

TABLE I: Dominant MPI collective functions for application benchmarks: HPC Challenge, OpenMX, and Graph 500.

|  |  | HPC Challenge |  | Open | Graph |
| --- | --- | --- | --- | --- | --- |
|  | STREAM | Random | FFT | MX | 500 |
|  |  | Access |  |  |  |
| MPI Bcast | √ |  | √ | √ |  |
| MPI Allgather |  |  |  |  | √ |
| MPI Allreduce | √ | √ | √ | √ | √ |
| MPI Reduce | √ |  |  | √ |  |
| MPI Alltoall |  | √ | √ |  |  |
| MPI Barrier | √ | √ | √ | √ | √ |

(G-RandomAccess), and Global Fast Fourier Transform (G-FFT). They are also used for the HPC Challenge Awards Competition. The global (G) designation denotes all processors communicate with each other by using MPI communication. The Embarrassingly Parallel (EP) designation denotes all processors can run simultaneously, but without any communication required between the processors.

G-HPL measures the floating point rate of execution for solving a linear system of equations. It is used to rank supercomputers for the Top 500 list. EP-STREAM Triad measures sustainable memory bandwidth and the corresponding computation rate of a triad vector operation. It requires no communication, and stresses local processor to memory bandwidth. G-RandomAccess measures the rate of integer updates to random locations in a large global memory array. The performance is measured in terms of giga-updates per second (GUP/s). It stresses all-to-all communication of small messages, that is, it is a latency-intensive program. G-FFT measures the floating point rate of execution of a double precision complex onedimensional Discrete Fourier Transform (DFT). It stresses all-to-all communication of large messages, that is, it is a bandwidth-intensive program.

We used HPCC version 1.4.3. The main parameters were set as follows: matrix size (Ns) is 1334619; block size (NBs) is 192; the number of processes (P x Q) is 40 x 64. With regard to G-FFT, we have faced a memory exhaustion problem of the Intel MKL when the problem size is larger than 80% of the physical memory in the preliminary experiment. G-FFT requires a bit of extra memory to perform the computations so the problem size of HPCC was limited to 80% of memory.

*3) OpenMX:* The OpenMX package [19], [20] is a software package designed for nano-scale material simulations. In this experiment, we used the OpenMX version 3.7.4. The execution times were measured for several steps of ab initio molecular dynamics simulations of an ionic liquid ([emim][TFSA]) [21]. The forces on the atoms were calculated by the density functional theory with norm-conserving pseudopotentials. Since it is hard to compare the performance with single problem size up to 128 nodes, we used three input data set files as follows: small (272 atoms, 5 steps), medium (2176 atoms, 3 steps), and large (4352 atoms, 3 steps). The total memory usages of small, medium and large input data sets are approximately 20 GB, 200 GB, and 400 GB, respectively.

*4) Graph 500:* The Graph 500 [22] traverses a large undirected graph in a breadth-first search, and it is a data intensive workload. It uses traversed edges per second (TEPS) as the

![](_page_2_Figure_7.png)

Fig. 1: MPI point-to-point throughput.

performance metrics. We used a reference code written in C with hybrid MPI and OpenMP. The version is 2.1.4. We measured three variants of the reference code: simple, replicatedcsr (compressed sparse row), and replicated-csc (compressed sparse column). The problem scale was set to 26, and this is the minimum problem size. Our preliminary experiment on a single node shows that a combination of two MPI processes and ten OpenMP threads achieves the best performance. Accordingly, we used this combination in the following experiment. To uniformly assign threads to processors, we used a rankfile which specifies the bindings of each MPI process to a CPU socket. In this experiment, we assigned two MPI processes to the respective CPU sockets on every node. And also, the environment variable OMP_NUM_THREADS was set to ten. Note that we found a problem whereby OpenMP threads are not properly assigned to processors without using a rankfile. In that case, the MPI processes did not get assigned to every processor. As a result, the validation process consequently could not be passed. This problem may be a defect in the Open MPI we used.

# IV. RESULTS

#### *A. Intel Micro Benchmark*

Figure 1 shows the point-to-point throughput by using PingPong benchmark program. The throughput improves as the message size increases from 1 byte to 4 MB. The peak throughputs of a physical cluster and a virtual cluster are 5991 MB/s and 5830 MB/s, respectively. The overhead of virtualization tends to be relatively smaller as the message size becomes larger. While the overhead with a 1 byte message is up to 25%, the overhead with a 1 MB message is less than 3%. Note that the theoretical bandwidth of FDR InfiniBand is 7000 MB/s, therefore, the MPI throughput reaches about 88% of the theoretical performance. The qperf benchmark, which uses InfiniBand Verbs API, performs at over 6400 MB/s on a physical cluster. Open MPI reduces 6% of the performance due to the overhead required.

Figure 2 shows the scalability of MPI collective functions, where the number of nodes increases from 2 to 128; the message size is fixed to 64 bytes, except for the Barrier measurement (Figure 2f). Generally speaking, the overhead of virtualization increases proportionally as the number of nodes

![](_page_3_Figure_0.png)

![](_page_3_Figure_1.png)

increases. This result shows a virtual cluster has a scalability issue. On a 2-node cluster, the execution time of Allgather, Allreduce, Reduce, Alltoall, and Bcast increases by 20%, 47%, 12%, 12%, and 17%, respectively. On a 128-node cluster, on the other hand, the execution time of Allgather, Allreduce, Reduce, Alltoall, and Bcast increases by 77%, 88%, 127%, 43%, and 99%, respectively. We have observed the same trend with the larger message sizes. On the contrary, the results of Barrier illustrate that the overhead is quite small, as shown in Figure 2f.

The results for Barrier are not intuitive. The execution time increases up to 64 nodes, and it unexpectedly drops on 128 nodes. Both a physical cluster and a virtual cluster show the same behavior. We pursued the cause of this behavior in such a way that we can consecutively incremented the number of nodes by one from 64 to 155. As a result, the execution time increases linearly until the number of nodes reaches 127, but it drops to one fifth as the number of nodes increases from 128 nodes onward. This may be considered because Open MPI changes the algorithms of Barrier depending on the number of nodes.

Figure 3 summarizes the relative execution time of collective benchmarks on a 128-node cluster normalized to the result of a physical cluster. The X-axis shows the message size, which is a multiple of four. The relative execution times grow up to two. Unlike the point-to-point throughput, the performance gap between a physical cluster and a virtual cluster does not decrease as the message size increases, but rather expands. With a 1 byte message size, all collective functions of a virtual cluster perform about 1.5 times slower than those of a physical cluster. With a 4 MB message size,

![](_page_3_Figure_5.png)

Fig. 3: Relative performance of IMB collective benchmarks with a 128-node cluster.

the relative performance varies from 1 to 2.

# *B. HPC Challenge*

Figure 4 shows the four benchmark results for HPCC. The larger the number, the better the performance. G-HPL on a 128 node-physical cluster achieves the performance 51.63 TFLOPS and 90% of the theoretical peak performance, as shown in Figure 4a. On the other hand, on a virtual cluster, it performs at 48.25 TFLOPS. The overhead of virtualization gradually increases as the number of nodes increases. The overheads of single node, 4-node, 16-node, 64-node, and 128-node clusters are 1%, 2%, 4%, 7%, and 6%, respectively.

EP-STREAM, as shown in Figure 4b, steadily achieves about 3.5 GB/s of memory bandwidth and it keeps a con-

![](_page_4_Figure_0.png)

Fig. 4: HPC Challenges.

stant performance level as the number of nodes increases. The performance is theoretically equivalent to the singlenode STREAM performance. While the results of a physical cluster are reasonable, those of a virtual cluster cluster show a mysterious outperformance by 20% with 4 and 16 nodes.

Figure 4c shows the result for G-RandomAccess. Both a physical cluster and a virtual cluster show the same trends on up to 4 nodes, but the results change when the number of nodes equal to 16 and over. A virtual cluster increases the performance, in contrast, a physical cluster decreases as the number of nodes increases.

In Figure 4d, the performance levels of G-FFT are roughly equal both on a physical and a virtual cluster. The performance gap becomes close as the number of nodes increases.

# *C. OpenMX*

The execution time of OpenMX with three input data sets is shown in Figure 5. The scalability of the large data set is not very good in contrast to that of other data sets, because the problem size is not large enough to fully utilize the CPU resources. The total memory usages of small, medium and large input data sets are approximately 20 GB, 200 GB, and 400 GB, respectively.

On both small and medium input data sets, the performance of a virtual cluster nearly close to that of a physical cluster. Sometimes a virtual cluster outperforms a physical cluster, e.g., small input data set on 4 nodes and medium input data set on 64 nodes. For large input data set, however, the execution time of a virtual cluster is slower than that of a physical cluster, by 120 seconds which corresponds to 22% of the overhead of virtualization. The computation per node is relatively small for the large input data set, and thus the overhead of communication becomes clearly visible.

# *D. Graph 500*

We measured three variants of the reference code: simple, replicated-csr, and replicated-csc. The replicated-csc shows the highest performance, and the trend is the same as that of the others. Therefore, we only show the results of the repliated-csc in Figure 6. The Y-axis shows the graph processing throughput in TEPS. The maximum number of nodes is 64 instead of 128, because the process crashed when we ran it on both 128-node physical and virtual clusters.

The performance improvement tends to saturate as the number of nodes increase. On a 4-node cluster, the performance improves by 3.0 times compared to the single node. On a 64-node cluster, in contrast, the performance only improves by 18.7 times. More importantly, the overhead of virtualization decreases as the number of nodes increases. The maximum result of 64 nodes is 6.36 GTEPS on a virtual cluster and 6.48 GTEPS on a physical cluster. In that case, the overhead is only 2%.

## V. DISCUSSION

# *A. Experimental setting*

Throughout our experiment, we have pinned the virtual CPUs to respective physical CPUs. We found that, without the

![](_page_5_Figure_0.png)

Fig. 5: OpenMX with three input data sets.

VCPU pinning, the performance of a virtual cluster is halved for almost all benchmarks. Without VCPU pinning, the Linux scheduler on the host OS dynamically change the mapping between a virtual CPU core and a physical CPU core, based on the load. This behavior affects HPC applications negatively. VCPU pinning statically binds the mapping so as to avoid cross-CPU socket memory transfer, which is the cause of the degradation in the inter-process communication performance.

There are many runtime parameters that can be used for tuning the MPI communication performance. Some are effective for some programs, but they affect other programs negatively. Therefore, we have decided to use Open MPI with the default parameter settings, including algorithms of collective functions. Nevertheless, some tuning parameters may be critical in general. For example, we have encountered a performance problem whereby Reduce is slower than AllReduce, and it can be fixed by disabling the runtime parameter mpi_leave_pinned. This setting can help to improve the network bandwidth in the case where large messages are repeatedly sent and received over RDMA with the same buffers. By disabling this option, Reduce shows a great improvement in performance, from 2 seconds to 6 milliseconds on a 128-node virtual cluster with a 4KB message size. Bcast also shows a great improvement in performance, from 55 milliseconds to 5.5 milliseconds. In contrast, Allgather and Alltoall show a decrease in the performance by half.

Although PCI passthrough is effective in improving the I/O performance of a virtual cluster, it is still unable to achieve the low communication latency of a physical cluster due to a virtual interrup injection, when VM Exit operations are involved, i.e., a world change between a guest OS and the host OS. This is because a guest OS cannot selectively intercept physical interrupts. Exit-less interrupt (ELI) [23] addresses this issue. It is a software-only approach for handling interrupts within guest VMs directly and securely. We expect that next-generation hardware virtualization, e.g., APICv, will significantly reduce the number of VM Exits at a virtual interrupt injection.

#### *B. Micro benchmarks*

We found that almost all MPI collective functions suffer from the scalability issue. The overhead of virtualization becomes significant as the number of nodes increases. We conjecture that the symptom originates from the inter-node

![](_page_5_Figure_7.png)

Fig. 6: Graph 500 replicated-csc with a scale of 26.

load imbalance introduced by the virtualization, and then the synchronization time at each iterative execution of a collective function becomes longer than that of a physical cluster. According to a recent report, Jose, et al. [8] have evaluated the performance impact of virtualization using SR-IOV with InfiniBand. They observed that MPI collective operations have a huge performance difference between virtual machines and physical machines, in accordance with our results described in Section IV. We have demonstrated this on a 128-node virtual cluster, whereas they used a 4-node small cluster environment. The situation gets worse on a large scale cluster.

# *C. Application benchmarks*

We also found that the overhead of virtualization has less impact on actual applications, if compared with micro benchmark programs. For HPCC results on a virtual cluster, the performance of G-HPL, G-FFT, and EP-STREAM Triad can closely equal the physical performance; the virtualization overhead on a 128-node cluster were about 6%, 2%, and 3%, respectively. They are a quite small amount of overhead in a large scale cluster. Both EP-STREAM Triad and G-RandomAccess can outperform the physical cluster. We have conducted more than three times additional experiments. The results show that these counterintuitive behaviors are reproducible. Although we have no clue to the behavior yet, the memory virtualization may play an important role. Both programs make a high demand on the memory subsystem, such as for TLB miss handling. Especially for G-RandomAccess, cache memory is ineffective and it can involve a lot of TLB misses. We suspect that the huge pages may more often be used on a virtual cluster compared with a physical cluster.

Lange, et al. [24] have demonstrated the performance of HPCC and other HPC applications on the Palacios hypervisor and the Kitten light-weight OS. They reported the virtualization overhead was less than 5% with nodes up to 4096 nodes. We have shown similar results on an HPC Cloud platform which consists of general purpose systems, i.e., Linux and KVM. Kudryavtsev, et al. [25] evaluated the performance of virtualized HPC applications compared to the physical cluster case. They showed the virtualization overhead of many tests from the HPCC and the NPB suite was less than 5%, but HPL and RandomAccess have performance overhead up to 30% and 15% respectively. Although the authors did not explore this issue in detail, they opined it can be caused by VCPU pinning, NUMA emulation, and/or the noise of the host OS.

# VI. CONCLUSION

The idea of HPC Clouds still has not become widely accepted for the HPC community, even through the overhead of virtualization can be dramatically reduced with the help of both hardware level and system software level virtualization mechanisms that are mature enough for practical use. In this paper, we have presented the impact of virtualization on our latest private cloud, which utilizes state-of-the-art research results on both virtualization and Cloud computing. Our private cloud provides a virtual cluster interconnected by InfiniBand for the users. We conducted a performance comparison on our private cloud. The performance is measured both on a physical cluster and a virtual cluster by using the Intel Micro Benchmark and some application level benchmark programs, including HPC Challenge, OpenMX, and Graph500. Our experimental results show almost all MPI collective functions suffer from the scalability issue, even though there is no gap in pointto-point throughput with a large message between a physical cluster and a virtual cluster. Fortunately, the negative impact is limited on application level benchmark programs, where the virtualization overhead is about 5%, even when the number of nodes grows up to 128. We suspect that the scalability issue on the collectives originates from the overwhelming repetition of the same function in the micro benchmark, which is less realistic in the actual HPC application.

Virtualization can contribute to system utilization improvements. We are considering two research directions as future work. The first one is the use of SR-IOV instead of PCI passthrough. Our system software is already ready to support it, and we plan to upgrade the firmware of the ConnectX-3 HCA. The second one is optimizing a VM placement algorithm based on the workloads of virtual clusters, such that a CPU intensive and an I/O intensive workloads are co-located on a single physical machine. Some researchers have tackled this problem, but it is still an open issue on actual HPC platforms.

## ACKNOWLEDGMENTS

This work was done during an internship at AIST, Japan. The authors would like to thank Assoc. Prof. Vara Varavithya, KMUTNB, and Dr. Yoshio Tanaka, AIST, for valuable guidance and advice. In addition, the authors would also like to thank the ASGC support team for preparation and trouble shooting of the experiments. This work was partly supported by JSPS KAKENHI Grant Number 24700040.

# REFERENCES

- [1] Apache cloudstack. [Online]. Available: http://cloudstack.apache.org/
- [2] P. Pornkitprasan, V. Visoottiviseth, and R. Takano, "Engaging Hardware-Virtualized Network Devices in Cloud Data Centers," in *Proc. ICT International Student Project Conference (ICT-ISPC2014)*, Mahidol University, Thailand, Mar. 2014, pp. 1–4.
- [3] T. L. Sterling, *Beowulf cluster computing with Linux*. MIT press, 2002.
- [4] P. Luszczek, E. Meek, S. Moore, D. Terpstra, V. M. Weaver, and J. Dongarra, "Evaluation of the HPC Challenge Benchmarks in Virtualized Environments," in *Proc. International Conference on Parallel Processing (Euro-Par2011)*, Bordeaux, France, Aug./Sep. 2012, pp. 436–445.
- [5] Y. Dong, X. Yang, J. Li, G. Liao, K. Tian, and H. Guan, "High Performance Network Virtualization with SR-IOV," *Journal of Parallel and Distributed Computing*, vol. 72, no. 11, pp. 1471–1480, Nov. 2012.

- [6] V. Mauch, M. Kunze, and M. Hillenbrand, "High Performance Cloud Computing," *Future Generation Computer Systems*, vol. 29, no. 6, pp. 1408–1416, Aug. 2013.
- [7] T. P. P. de Lacerda Ruivo, G. B. Altayo, G. Garzoglio, S. Timm, H. W. Kim, S.-Y. Noh, and I. Raicu, "Exploring Infiniband Hardware Virtualization in OpenNebula towards Efficient High-Performance Computing," in *Proc. SCALE Challenge of the IEEE/ACM CCGrid2014*, Chicago, Illinois, USA, May 2014.
- [8] J. Jose, M. Li, X. Lu, K. C. Kandalla, M. D. Arnold, and D. K. Panda, "SR-IOV Support for Virtualization on InfiniBand Clusters: Early Experience," in *Proc. IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing (CCGrid2013)*, Delft, Netherlands, May 2013, pp. 385–392.
- [9] M. Caballer, C. D. Alfonso, F. Alvarruiz, and G. Molto, "EC3: Elastic ´ Cloud Computing Cluster," *Journal of Computer and System Sciences*, vol. 79, no. 8, pp. 1341–1351, Dec. 2013.
- [10] G. Juve and E. Deelman, "Automating Application Deployment in Infrastructure Clouds," in *Proc. IEEE International Conference on Cloud Computing Technology and Science (CloudCom2011)*, Washington, DC, USA, 2011, pp. 658–665.
- [11] MIT, StarCluster. [Online]. Available: http://web.mit.edu/stardev/ cluster/
- [12] F. Doelitzscher, M. Held, C. Reich, and A. Sulistio, "ViteraaS: Virtual Cluster as a Service," in *Proc. IEEE International Conference on Cloud Computing Technology and Science (CloudCom2011)*, Athens, Greece, Nov. 2011, pp. 652–657.
- [13] P. Marshall, K. Keahey, and T. Freeman, "Elastic Site: Using Clouds to Elastically Extend Site Resources," in *Proc. IEEE/ACM International Conference on Cluster, Cloud and Grid Computing (CCGrid2010)*, Melbourne, Victoria, Australia, May 2010, pp. 43–52.
- [14] P. Marshall, H. T. M., K. Keahey, D. L. Bissoniere, and M. Woitaszek, "Architecting a Large-scale Elastic Environment - Recontextualization and Adaptive Cloud Services for Scientific Computing," in *Proc. International Joint Conference on Software Technologies (ICSOFT2012)*, Rome, Italy, Jul. 2012, pp. 409–418.
- [15] R. S. Montero, R. Moreno-Vozmediano, and I. M. Llorente, "An Elasticity Model for High Throughput Computing Clusters," *Journal of Parallel and Distributed Computing*, vol. 71, no. 6, pp. 750–757, Jun. 2011.
- [16] Open MPI. [Online]. Available: http://www.open-mpi.org/
- [17] Intel Micro Benchmark. [Online]. Available: http://software.intel.com/ en-us/articles/intel-mpi-benchmarks
- [18] P. Luszczek, J. J. Dongarra, D. Koester, R. Rabenseifner, B. Lucas, J. Kepner, J. McCalpin, D. Bailey, and D. Takahashi, "Introduction to the HPC Challenge Benchmark Suite," Tech. Rep., Mar. 2005.
- [19] Open Source Package for Material eXplorer. [Online]. Available: http://www.openmx-square.org/
- [20] T. Ozaki, "Variationally Optimized Atomic Orbitals for Large-Scale Electronic Structures," *Physical Review B*, vol. 67, p. 155108, Apr. 2003.
- [21] S. Tsuzuki, W. Shinoda, H. Saito, M. Mikami, H. Tokuda, and M. Watanabe, "Molecular Dynamics Simulations of Ionic Liquids: Cation and Anion Dependence of Self-Diffusion Coefficients of Ions," *Journal of Physical Chemistry B*, vol. 113, no. 31, pp. 10 641–10 649, Jul. 2009.
- [22] Graph 500. [Online]. Available: http://www.graph500.org/
- [23] A. Gordon, N. Amit, N. Har'El, M. Ben-Yehuda, A. Landau, A. Schuster, and D. Tsafrir, "ELI: Bare-metal Performance for I/O Virtualization," in *Proc. ACM International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS 2012)*, Mar. 2012.
- [24] J. R. Lange, K. Pedretti, P. Dinda, P. G. Bridges, C. Bae, P. Soltero, and A. Merritt, "Minimal-overhead Virtualization of a Large Scale Supercomputer," in *Proc. ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE2011)*, Mar. 2011, pp. 169– 180.
- [25] A. Kudryavtsev, V. Koshelev, and A. Avetisyan, "Modern HPC Cluster Virtualization using KVM and Palacios," in *Proc. Annual International Conference on High Performance Computing (HiPC2012)*, Pune, India, Dec. 2012, pp. 1–9.

