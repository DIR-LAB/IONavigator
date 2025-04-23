# *Evaluating Effect of Write Combining on PCIe Throughput to Improve HPC Interconnect Performance*

Mahesh Chaudhari HPC-Technologies Group *Centre for Development of Advanced Computing*  Pune, India maheshc@cdac.in

Kedar Kulkarni HPC-Technologies Group *Centre for Development of Advanced Computing*  Pune, India kulkarni.kedar.r@gmail.com

Shreeya Badhe HPC-Technologies Group *Centre for Development of Advanced Computing*  Pune, India shilpav@cdac.in

Dr. Vandana Inamdar Dept. of Computer Engineering and Information Technology *College of Engineering, Pune*  Pune, India vhj.comp@coep.ac.in

*Abstract***— HPC interconnect is a very crucial component of any HPC machine. Interconnect performance is one of the contributing factors for overall performance of HPC system. Most popular interface to connect Network Interface Card (NIC) to CPU is PCI express (PCIe). With denser core counts in compute servers and increasingly maturing fabric interconnect speeds, there is need to maximize the packet data movement throughput between system memory and fabric interface network buffers, such that the rate at which applications (CPU) generating data is matched with rate at which fabric consumes the same. Thus PCIe throughput for small and medium messages (Programmed Input/Output) needs to be improved, to synchronize with core processing rate and fabric speeds. And there is scope for this improvement by increasing the payload size in Transaction Layer Packet (TLP) of PCIe. Traditionally, CPU issues memory writes in 8 bytes (payload for TLP), underutilizing the PCIe bus since overhead compared to payload is more. Write combining can increase the payload size in TLP, leading to more efficient utilization of available bus bandwidth, thereby improving the overall throughput.** 

**This work evaluates the performance that could be gained by using Write Combine Buffers (WCB) available on Intel CPU, for send side interface of HPC interconnect. These buffers are used for aggregating the small (usually 8 bytes) memory mapped I/O stores, to form the bigger PCIe Transaction Level Packets (TLP), which leads to better bus bandwidth utilization. It is observed that, this technique improves peak PIO bandwidth by 2x compared to normal PIO. It is also observed that till 4096 bytes write combine enabled PIO outperforms DMA.**

#### *Keywords— HPC interconnect; write-combining; Network I/O; PCI bus bandwidth.*

### I. INTRODUCTION

Cluster based HPC system is mainly comprised of three components: high end compute server, high performance fabric interconnect, and highly optimized software. Compute server is densely populated with more core count, large system memory and efficient I/O buses. System Software, parallel programming library, installation and execution scripts, statistics monitoring daemons etc. are bundled in the software suite for HPC system. Metrics for evaluating/measuring the performance of fabric interconnect is bandwidth in bytes per second, latency in micro second and message rate in million messages per second. Optimizations at all levels and all components of HPC interconnect, are required to achieve the competitive performance. Send side interface (between host and NIC), fabric and receive side interface (between NIC and host) broadly constitutes any HPC fabric interconnect. Improvement in send side interface is desired in this work.

Function of send side interface is to pass the application data (may or may not be packetized) to the Network Interface Card (NIC) for sending out packetized data through the fabric to the destination node. There are two ways this I/O is performed in system: Programmed Input/output (PIO) and Direct Memory Access (DMA). Applications adapting message passing as their Inter Process Communication (IPC) generally has two types of messages to share, latency sensitive small messages (in bytes) and bandwidth hungry bulk transfers (in Megabytes). Choosing the I/O mode according to the message size can improve the performance. Threshold, where mode of I/O needed to be switched from PIO to DMA should be set very optimally to gain maximum performance. This work also derives this threshold for HPC interconnect.

Write Combine (WC) technique allows non-temporal streaming data to be stored temporarily in intermediate buffers, to be released together later in burst instead of writing in small chunks to the destination. Destination may be next level cache or system memory or I/O memory. Intel CPU contains special buffers called Write Combine store buffers to ease the L1 data cache miss penalty. When a memory region is defined as WC memory type, memory locations within this region are not cached and coherency is not enforced. Speculative reads are allowed and writes may be delayed. Thus, WC is most suitable for applications, in which, strongly ordered un-cached reads, but weakly ordered streaming stores are required, such as graphics applications and network I/O.

# II. RELATED WORK

Similar work on improving the I/O bus bandwidth is done by Steen Larsen and Ben Lee, in which they have compared the throughput achieved, using dma based descriptor vs using write-combined PIO [1]. This work differs from Larsen's work [1] with following differences. First, this work deploys direct user I/O, i.e. user application can directly PIO writes data without going through kernel, saving the context switch penalty. Issue with bypassing kernel is sharing problem, which

causes contention between multiple processes for shared hardware queues. However this problem is taken care by allocating the separate queues to all contending processes, so that each user will have exclusive access to the queue owned by it. Second, PCIe Gen2 x8 link used in this work overcomes the 1 GB/s theoretical limitation presented by x4 PCIe Gen1 bus in [1]. Third, hardware developed for this work is custom I/O Adapter, not the standard Ethernet or InfiniBand adaptor.

#### III. PROPOSED METHOD

Traditionally, PIO writes are executed in 8 bytes chunks since CPU issues them in 8 bytes. Problem with this is inefficient use of PCI bandwidth since transaction layer overhead of PCIe stack is 20-24 bytes for 8 bytes payload. In write combining, small PIOs to same cacheline are buffered into separate buffers in Intel CPU and full cacheline transfers happens over the PCIe instead of partial cacheline transfers. This same technique is exploited in this work to do network I/O. This is achieved by declaring I/O memory on hardware device as write combine memory type. I/O memory is mapped directly to address space of user application, with writecombine attribute set. Small (8 bytes) I/O by application is buffered into write-combine buffers (a.k.a. fill buffers) on CPU core, till the buffer is full. Once buffer is full, it is evicted to destination memory automatically. Timings, to calculate Bandwidth, are measured by reading Time Stamp Counter (TSC) register on CPU core, using rdtscp instruction [3]. TSC is calibrated first, for our test system before use. For our test machine TSC is clocking at the frequency of 2.6025GHz. Overhead of reading TSC register is 44 TSC cycles which is subtracted from readings to get pure PIO write time. Other system noise is also avoided to prevent diluting the readings. To avoid the context switch penalty, in-house developed benchmark process is pinned to same core. Core is exclusively owned by the benchmark process to prevent sharing the core by other processes. Hardware interrupts are disabled for the corresponding core. Tests are repeated 1000 times and average of readings within mean + standard deviation (μ + ı) is considered as final reading.

 This work also requires development of simple PIO controller in custom I/O adapter. Logic in this device processes PIO requests received from CPU over PCIe bus. This adaptor has 2KB of on board memory available for user access.

## IV. EXPERIMENTAL SETUP

Experiments for this work are carried out over the Intel Xeon E5-2650 v2, Sandy Bridge based 16 cores (2 threads per core) clocked at 2.6GHz. Required custom I/O adaptor is implemented on Xilinx Kintex 7 FPGA KC705 evaluation kit operated at 250MHz. This custom I/O adapter is interfaced to CPU over PCIe Gen2 interface. CentOS 6.4 (2.6.31-358 kernel) distribution of linux is used to operate the test server.

# V. OBSERVATIONS AND ANALYSIS

It can be seen from the figure 1 that 2x improvement is achieved in peak bandwidth (2.49 GB/s at 64 bytes) for write combine enabled PIO against peak bandwidth (1.182 GB/s at 32 bytes) for normal PIO. Write combine enabled PIO bandwidth saturates at 665 MB/s (for data size >64KB), while normal PIO bandwidth saturates to 60 MB/s (for data size>512B). Nearly 11x improvement is observed in sustained bandwidth for write combine enabled PIO against normal PIO. Figure 1 also shows that write combine enabled PIO outperforms the DMA till message size less than 4096 bytes.

Peak bit rate of x8 Gen2 PCIe link is 40 Gb/s. Physical layer encoding reduces it by 20% (=32 Gb/s or 4 GB/s). Transaction layer overhead (24B header for 64B data) further limits it to 72.7%. Thus practically achievable throughput is 2.88 GB/s.

![](_page_1_Figure_10.png)

**Figure 1 Bandwidth comparison of Write Combine enabled PIO vs Normal PIO vs DMA** 

#### VI. CONCLUSION AND FUTURE WORK

Write combined PIO can be used to transfer small and medium messages (till 4KB) from system memory to NIC buffers for across node IPC. DMA is still suitable as network I/O mode for large messages(>4KB).

There is still scope for improvement as we could achieve ~87% of practically possible peak bandwidth of x8 PCIe gen2 link. Following optimizations can be tried to extract more out of PCIe. Parallel version of in-house developed benchmark can be implemented in which, multiple threads or processes of benchmark is spawned; each thread (process) pumps data over PCIe link to their exclusively owned memory on hardware. All of them aggregately might saturate the PCIe link. Pipelining PIO writes across all available write combine buffer (if not happening implicitly) can also present scope for performance improvement. Non-temporal version of data movement instruction which bypasses L1 and L2 lookups, may also contribute to saturate link [2]. Also, experiments can be repeated over more advanced configuration like PCIe Gen3 interface and Haswell platform, to evaluate the performance.

# REFERENCES

- [1] Steen Larsen and Ben Lee, "Reevaluation of Programmed I/O with Write-Combining buffers to Improve I/O Performance on Cluster Systems," International Conference on Networking, Architecture and Storage (NAS), Aug 2015.
- [2] Liang-min Wang, "How to Implement a 64B PCIe* Burst Transfer on Intel® Architecture," Feb 2013.
- [3] Gabriele Paoloni, "How to Benchmark code execution times on Intel IA-32 and IA-64 ISA", White paper by Intel, Sept 2010.

