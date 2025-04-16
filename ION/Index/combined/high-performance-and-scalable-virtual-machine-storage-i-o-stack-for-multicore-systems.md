# High Performance and Scalable Virtual Machine Storage I/O Stack for Multicore Systems

Diming Zhang∗†, Hao Wu∗, Fei Xue∗, Liangqiang Chen∗ and Hao Huang∗

∗Department of Computer Science & Technology, Nanjing University

Nanjing Jiangsu, China 210023

Email: diming.zhang@gmail.com, hhuang@nju.edu.cn

†School of Computer Science & Engineering, Jiangsu University of Science and Technology

Zhenjiang Jiangsu, China, 212003

Email: diming.zhang@gmail.com

*Abstract***—Today extending virtualization technology into highperformance, cluster platforms generates exciting new possibilities, including dynamic allocation of resources to job, easier to share resources between different jobs, easy checkpointing of jobs, and deployment of job-specific work environment. However, there still exists an I/O scalability problem in virtualization layer which may impede virtualization technology to be widely used in high-performance computing. Because we meet a sharp performance degradation when a virtual machine uses the multiqueue high performance non-volatile storage device as the secondary storage. Such a problem is caused by the current virtual block I/O layer which uses only one I/O thread to handle all I/O operations to a virtualized storage device. As the number of I/O intensive workloads increases, the rate of mutex contention of the I/O thread is accelerated because only one of them is allowed to run at any given instant. Therefore, it is the key problem that should be settled immediately so as to improve block I/O performance in virtualization. In this paper, we propose a novel design of high performance block I/O stack to solve this problem. The workloads will be free of the I/O contention inside the hypervisor by using the proposed method which uses multithreaded I/O threads to handle all I/O operations to one storage device in parallel. Meanwhile, we use switch-less mechanisms to reduce the overhead caused by sending notification between a VM and its hypervisor; and improve I/O affinity by assigning a distinct dedicated core to each I/O thread in order to eliminate unnecessary scheduling. The prototype system is implemented on Linux 3.19 kernel and Quick Emulator (QEMU) 2.3.1. We deploy it to the POWER8 server for a detailed evaluation. The experimental results show that the proposed architecture scales graciously with multi-core environment. For example, test on 10-ways parallel I/O intensive workloads gets an 800% increase than the single core implementation, indicating that the block I/O performance in a virtual machine is close to that of a bare metal system.**

*Index Terms***—igh-performance, Block I/O, Scalability, Multithreaded, Virtualizationigh-performance, Block I/O, Scalability, Multi-threaded, VirtualizationH**

## I. INTRODUCTION

Current High-Performance Computing (HPC) workloads are impacted by performance and latency problems. Hence, using the high performance storage device is regarded as a more cost-efficient choice. Today, the Non-Volatile Memory Express (NMVe) based solid state drive (SSD) brings almost 3 Gbps of read bandwidth due to its multiqueue parallel I/O design[1]. Increasingly, organizations are finding that the lag of block I/O architecture has become the bottleneck of the high performance system[2]. Therefore, they start to focus on using multi-threaded technology to mitigate the mismatch between the high performance storage device and the block I/O layer [3]. However, such a mismatch is still severe in virtualization if people plan to use the virtual machine (VM) to run multiple I/O intensive workloads concurrently. Because studies on how the high performance non-volatile storage affects the virtualization requirements are very few. The hypervisor's storage stack, a.k.a. block layer, is not properly parallelize-supported so that at any given instant only one of I/O workloads accessing the same storage device is actually running, regardless of multiqueue feature of the underlying high performance storage device.

In this paper, we propose a novel high performance and scalable I/O stack for virtualization to solve this problem. The proposed method focuses on enhance I/O parallelism feature for the virtualization layer. Our design is based on paravirtual I/O model [4], [5], and provides benefits in three ways. First, we ensure each block I/O workload able to access the same storage device in parallel, all block I/O workloads are distributed across multiple threads and therefore to multiple cores. Second, we use efficient I/O notification mechanism, which enables VMs to communicate with its hypervisor with very low overhead. Third, we optimize I/O scheduling by using I/O affinity strategy.

We implemented the prototype based on Kernel-based Virtual Machine (KVM) which is widely used in many Linux distributions as a kernel module to provide virtualization feature. For performance profiling, we did detailed measurements on both a null block device and a physical high performance NVMe storage device on our POWER8 server. The null block device can mimic a virtual storage device by receiving block I/O requests and acknowledging completions instantly. And we further demonstrate the proposed system by experiments on real devices. The experimental results show that our design scales graciously in multi-core environment. For example, test on 10-ways parallel I/O intensive workloads gets an 800% increase than the single core implementation, indicating that the block I/O performance in a virtual machine is close to that of a bare metal system.

![](_page_0_Picture_16.png)

978-1-5386-2129-5/17/31.00 ©2017 IEEE DOI 10.1109/ICPADS.2017.00047

Although we only implement our design based on KVM and POWER8 architecture, it is not limited the specific system but rather generally applicable. A group of patch sets generated from our prototype have been merged into the upstream Linux kernel. In summary, the contribution of this paper is threefold:

- ∙ First, we propose a novel design that uses multiple dedicated I/O threads to improve the block I/O middle service layer between a VM and its hypervisor in multicore environment.
- ∙ Second, we also use switch-less notification mechanism and configure I/O affinity in order to further optimize the performance.
- ∙ Third, we present detailed and comprehensive performance evaluation to show that the prototype system achieves stable performance and scalability improvement compared to the original.

The rest of the paper is organized as follows: Section II reviews the current implementation of the KVM storage stack and its performance limitations. Section III presents our design, as well as two performance optimizations. We discuss some implementation details in Section IV. We describe the experimental methodology in Section V and present detailed experimental results in Section VI. Related work is introduced in Section VII. Finally, we conclude our work in Section VIII.

#### II. BACKGROUND

In this section, we introduce some background about the hypervisor block I/O layer, and reveal the bottleneck of the current block I/O layer in virtualization basing on a specific benchmark-driven analysis.

### *A. The Paravirtual I/O Framework*

Hypervisor is a middleware that, on the one hand, allows VMs to access diverse storage devices in a uniform way. And on the other hand, provides storage devices and drivers with a single point of entry from VMs. Paravirtualization is a virtualization technique that presents a software interface to virtual machines that is similar, but not identical to that of the underlying hardware.

The paravirtual I/O framework allows the guest OS to run some specialized codes to cooperate with its hypervisor, improving the I/O performance. For example, *virtio* is a paravirtual I/O framework for KVM, which presents several ring buffers transport organized as one or more *virtqueues* and device configuration as a PCI (Peripheral Component Interconnect) device. The paravirtual block I/O driver, *virtio*blk, is implemented by *virtio*. It places pointers to buffers on the *virtqueue* and uses Programmed I/O (PIO) command to initiates block I/O requests. Moreover, the efficient is further improved because the hypervisor can directly access *virtqueues* from the memory of guest OS without copying (zero-copy [6]). Paravirtualization requires its *front-end* driver to be installed in the guest OS. The *front-end* driver sends each I/O request to the hypervisor's *back-end* driver which handles the arriving request and later returns a reply.

![](_page_1_Figure_10.png)

Fig. 1. Benchmark analysis on the VM and the bare metal system. The hypervisor is KVM with *virtio-data-plane* paravirtual I/O driver. The parameters of FIO workloads are 4KB, random read direct I/O, 32 iodepth, libaio and jobs=N. Each job is assigned to a dedicated vCPU and reads the same *null-blk* device. The results show that there is a large performance gap between the VM and the bare metal.

In multicore environment, some research results [7], [8], [9], [10] have been shown that performance can be improved by assigning a dedicate core for the I/O thread, rather than timesharing the same core for both the guest OS and its I/O thread. Using a dedicate core to handle the I/O thread not only leaves the virtual core of the VM with more cycles, it also improves overall efficiency because context switches are avoided.

## *B. Bottleneck of the Paravirtual I/O Framework*

Although paravirtual I/O is the most popular I/O virtualization method at present, we notice that its performance still significantly lags behind that of bare-metal in some conditions. For instance, we find that *virtio-data-plane*, a current stateof-the-art paravirtual I/O framework for block I/O, shows a significant scalability issue leading to performance degradation in the context of accessing a single high performance nonvolatile storage device.

Figure 1 shows our measurements of the *virtio-data-plane* performance. To evaluate its effectiveness in the context of accessing single high performance non-volatile storage device, we used the *null-blk* device to mimic the high-performance storage device. We did comparative tests between the VM which has 10 virtual CPUs (vCPUs) and bare-metal system respectively. The Flexible I/O Tester (FIO) was used to generate block I/O workloads for measurements. We noticed a large performance gap between the VM and the bare-metal system, as shown in Figure 1(a). The more FIO workloads we executed simultaneously, the bigger performance gap we met. Figure 1(b) shows that the latency of the block I/O operation from the VM grows up with the increase in the number of parallel execution of FIO workloads. While the experimental result of the bare-metal system seems that it has no scalability problem on running FIO workloads in parallel. It is obvious that the *virtio-data-plane* cannot afford heavy I/O intensive workloads, because I/O throughput significantly decreased when we executed multiple I/O intensive workloads in the VM.

## III. DESIGN

In this section, we present our proposition for an High Performance and Scalable Virtual Machine Storage I/O Model. The proposed method is based on the paravirtual I/O framework, improving on its performance and scalability by avoiding the mutex contention associated with I/O threads, and providing a novel parallel mechanism, allowing multiple I/O threads to serve one multi-queue storage device together. The proposed method can be applied to diverse paravirtual I/O implementation in different hypervisors.

# *A. Architecture*

The core insight to improve block I/O scalability in virtualization is to alleviate the mutex contention caused by the only one I/O thread of each storage device. As shown in Figure 2, compared to Baseline, our design supports multiple submission queues, called virtual queues, in one paravirtual storage device. Because, rather than gathering I/O for dispatch in a single submission queue, the proposed method maintains block I/O requests in a set of virtual queues. These virtual queues can be configured so that each virtual queue is assigned to a physical core on the system. For example, on a NUMA system that has 20 cores and 2 sockets, the queues can range between 2 and 20.

For the VM, a group of virtual queues in the paravirtual driver can mimic behavior of a multiqueue block device, for example, the NVMe SSD which is widely common used by enterprises at present. Because each virtual queue is considered as a distinct I/O entry of the virtual device so as to provide the multiqueue feature. This ensures that the block I/O layer of the guest OS can handle I/O requests in parallel, just like an OS that accesses multiqueue block device in the non-virtualized environment.

This new block layer can reorder I/O operations from the VM by using these virtual queues so that it can gather lager I/O requests and then sends them down into the underlying storage device. Moreover, by using multiple virtual queues as a staging area, the hypervisor allows its block layer to adjust the submission rate for quality of service (QoS) or due to device back pressure informing the hypervisor should not submit additional I/O or risk of buffer overflow. In the meanwhile, each virtual queue takes advantage of its own dedicated I/O thread to send requests down into one of underlying hardware queues.

The storage device I/O entries are mapping to multiple hardware queues in the block layer of hypervisor. Hardware queues residing in the hypervisor's block layer are introduced to receive I/O requests from the virtual queues. The number of hardware queues are typically match the number of hardware contexts provided by the block device specific driver. For example, most SATA- or SAS-based SSDs support only one submission and completion queue, while the advanced NVM Express (NVMe) interface may support a flexible number of submission queues and completion queues[11].

In addition, each virtual queue is allowed to feed a random idle hardware queue, with no need to maintain a global ordering. Because I/O ordering already has done in the guest OS. Therefore, each hardware queue can be directly assigned to a dedicated physical core or NUMA node to provide a fast I/O path from the paravirtual back-end driver to its storage device.

## *B. Switch-less Notification Mechanism*

In paravirtual I/O model, the *front-end* driver puts its I/O requests into a shared memory region. The *back-end* driver then notifies the I/O thread that new work is ready. The POWER8 architecture provides a light-weight architectural mechanism, *guest to host IPI*, to send notification between a VM and its hypervisor. By adopting this hardware feature, we can search for a core running in the hypervisor and send it an IPI message to be handled. This avoids the context switch for the notification which would improve I/O performance of virtual devices, especially in the multicore environment.

However, Some architectures do not have a similar *guest to host IPI* mechanism have to perform an *exit* (trap into the hypervisor) form the guest OS to interrupt a hypervisor's thread. This kind of *exit* causes a large amount of context switching overhead. Most recent studies [12], [13], [14] showed that overheads in I/O virtualization were mainly caused by context switches. Therefore, we can eliminate this overhead by polling in the hypervisor's core [15]. The polling technique has been used in various ways to improve system performance [16], [17]. In this case, after the *front-end* driver putting its requests into the memory buffer shared with the hypervisor, the guest OS does not need to employ an *exit* to notify the hypervisor. The hypervisor voluntarily polls the shared memory from the dedicated core, handling requests as long as they are noticed. Similarly, instead of traditional interrupts in the guest OS, the dedicated I/O thread in the guest OS checks the reply by polling, and completes I/O workflow.

Note that polling mechanism needs a dedicated core to serve each I/O thread. However, for workloads are not I/Ointensive, the costs inherent in frequent polling will outweigh the benefits of switch-less notification mechanism. Therefore, it is beneficial to switch freely between the new switch-less mechanism and the old *exit*-based notification mechanism, according to the actual situation.

## *C. I/O Affinity*

Most previous studies asserted that one I/O thread can make full use of the hardware performance [15], [18]. However, in recent years that have changed when the NVMe SSD existed. The traditional approach to handle I/O requests by only one separate I/O thread per storage device and let the hypervisor schedule these I/O threads on one core is insufficient.

The traditional I/O scheduling in virtualization is threadbased. This scheduling mechanism may lead to delay I/O response, because a core is likely to provide services to another job for a long time until the hypervisor decides to schedule it.

In our design, the I/O scheduling is designed to achieve better affinity and scalability, utilizing a more efficient approach to I/O scheduling: each I/O thread runs on an dedicated core,

![](_page_3_Figure_0.png)

Fig. 2. This figure describes the difference between the proposed architecture and *virtio-data-plane* which is the state-of-the-art paravirtual block I/O framework. The proposed method makes use of multiple virtual queues to receive I/O requests from the VM, and uses a group of dedicated I/O threads to establish communication between the VM and the underlying storage device in order to keep parallelism.

and handles the I/O requests of a single virtual queue. Figure 3 illustrates how I/O scheduling works: When a VM has one or more I/O-intensive workloads, the same number of cores can inspect the virtual queues they are serving without latency, keeping fairness and parallelism. Moreover, By assigning a dedicated core per I/O thread, the cache miss rate and the scheduling overhead caused by unnecessary context switch may decrease. And the benefits of I/O affinity are even more pronounced when the I/O thread utilizes switch-less notification mechanism.

# IV. IMPLEMENTATION

We implemented the prototype based on KVM to validate its functionality. KVM is open source software that turns Linux kernel into a hypervisor. KVM consists of a loadable kernel module and its userspace component included in QEMU. The *virtio* protocal is used in KVM to offer the paravirtul I/O service. We modified both KVM and its *virtio* paravirtual driver inside QEMU. In addition, although the hardware architecture we used is POWER8, it is not limited the specific hardware but rather generally applicable. Furthermore, some patch sets generated from our work has been merged into the mainline Linux Kernel development tree.

#### *A. Paravirtual I/O Protocol*

KVM offers features of block I/O paravirtualization by using *virtio-blk*, which is derived from a paravirtualization framework initiated by IBM [4]. In our implementation, the changes in the current *virtio* framework mainly include:

- ∙ Normally, the *virtqueue* is a mechanism for bulk data transport on virtio devices [19]. Basing on the queue number configuration, we allocate the number of *virtqueues* in one *virtio-blk* device. Typically, the number of *virtqueues* equals the vCPU numbers minus one, due to at least one vCPU has to be separated to handle events other than I/O.
![](_page_3_Figure_8.png)

![](_page_3_Figure_9.png)

VM and I/O thread-based scheduling for all cores

![](_page_3_Figure_11.png)

Fig. 3. Comparing our I/O affinity strategy to the native thread-based scheduling.

- ∙ Modify QEMU's block layer so that it can processes each *virtqueue* in the different I/O thread. This is an important step to handle block I/O in parallel.
- ∙ Assign each *virtqueue* a Message Signaled Interrupts Extended (MSI-X) [20] vector. And bind each *virtqueue* to a dedicated vCPU by setting the MSI-X IRQ affinity

for the *virtqueue*.

It is important to note that QEMU's block layer does not support multiple *virtqueues* yet. Because each *BlockDriver-State* of a storage device is associated with an AioContext using *bdrv* set aio *context()* and *bdrv* get aio *context()*. This allows block layer code to process I/O inside the right *Aio-Context*. Therefore, the *virtio-blk* device still processes all *virtqueues* in the same *AioContext*.

In our implementation, we divide the *queue-state* inside the native *BlockDriverState* into multiple independent *per-queuestates* for the *virtio-blk* device, and binds each *virtqueue* of the *virtio-blk* device to one of *per-queue-states*. To do this, each *virtqueue* has its own *queue-state* inside the *BlockDriverState* so that each I/O thread may access the *BlockDriverState* in parallel.

To improve the efficiency of MSI-X, in POWER8 architecture, we enabled XICS fast path for irqfd-generated interrupts. Since we can easily generate virtual interrupts on XICS without having to do anything worse than take a spinlock, we define a kvm *arch* set irq *inatomic()* for XICS, and also remove kvm set *msi()* because it is not used any more. It was found to significantly help guest's I/O performance by around 30%.

## *B. Switch-less Notification Mechanism*

In KVM, the guest executes a PIO instruction which causes a heavy weight *exit* on context switch to notify its host of new coming I/O requests. The proposed method avoids these *exits* by replacing these notifications with the *guest to host IPI* mechanism in POWER8 architecture.

We tried to walk through KVM *FAST MMIO* BUS at the beginning of *kvmppc* hv *emulate mmio()*, thus we can look up the *eventfd* directly, bypassing instruction emulation. This will benefit *MMIO* notification for *virtio* specification 1.0. By exporting icp *send hcore msg()* and *find available hostcore()*, we can take advantage of the guest to host IPI mechanism implemented for the vCPU wakeup in H IPI to ask some host cores to do *Fast MMIO* and bypass traditional *MMIO* code path. Then, KVM must set the rm *action* to *XICS* RM *FAST MMIO* and rm *data* in real mode (In real mode the top 4 bits of the address space are ignored) to point to the vCPU which stores the *FAST MMIO GPA/STATE* before sending the IPI. We added support to realmode KVM to search for a core running in the host partition and send it an IPI message with *FAST MMIO GPA* to be handled. This avoidance of the context switch for the *FAST MMIO* access improves I/O performance of *virtio* devices, especially when Simultaneous Multithreading (SMT) mode is on.

For better performance, we adopt some timeout mechanisms in case that there are some delays on host core's IPI handler in some heavy workload case. And we also keeps a per-vCPU cache for recently page faulted *MMIO* entries. On a page fault, if the entry exists in the cache, we can avoid some time-consuming paths, then directly call *kvmppc* hv *emulate mmio()*. In current implement, we limit the size of cache to four. Because it is enough to cover the high-frequency *MMIO HPTEs* in most case.

Additionally, for other hardware architectures that do not have switch-less notification mechanism like *guest to host IPI*, they can use polling-based I/O threads to avoid these *exits*. It is important to make polling be as efficient as possible, to ensure that unsuccessful polling of idle *virtqueues* does not significantly hurt performance of other *virtqueues*. Hence, we may add new halt polling vCPU stats which are used to collect information about a vCPU. The stats *halt attempted poll* and *halt successful poll* are used to keep track of the number of times the vCPU attempts to and successfully polls. Since these stats are summed over all the vCPUs for all running guests it doesn't matter which vCPU they are attributed to, thus we choose the current runner vCPU. And by adding new vCPU stats: *halt poll success* ns, *halt poll fail* ns and *halt wait* ns to be used to accumulate the total time spend polling successfully, polling unsuccessfully and waiting respectively, and *halt successful wait* to accumulate the number of times the vCPU waits. Given that *halt poll success* ns, *halt poll fail* ns and *halt wait* ns are expressed in nanoseconds it is necessary to represent these as 64-bit quantities, otherwise they would overflow after only about 4 seconds.

Since the time spends polling or waiting should be known, it is possible to determine the average poll and wait times. This will give the ability to tune the KVM module parameters based on the calculated average wait and poll times. Basing on these new vCPU stats of polling, we introduce new halt polling functionality into the KVM. When a vCPU is idle, it will be used to poll for some period of time before scheduling itself out.

## *C. I/O Affinity*

We assign one I/O thread to a dedicated core, so that each thread may handle its own *virtqueue* separately. One of the challenges of implementing the proposed I/O scheduling strategy is deciding which cores should be assigned to I/O threads. Because today's multicore platforms have a multisocket, or Non-uniform Memory Access (NUMA), design where portion of memory is closer to some of cores. On such platforms, the overall performance is optimal if a VM running on a specific socket is serviced by I/O threads running on the same socket too. In addition, it is certain that the *virtqueues* shared between the VM and I/O threads associate with it are surely allocated from memory belongs to this socket.

In our implementation, each I/O thread is configured to handle only one *virtqueue*, and both of them are associated with the same socket in order to ensure that a VM does not spread across more than one socket by restricting its vCPU thread to just run on cores inside one socket. Furthermore, the prototype not only pins I/O threads to different cores, but direct interrupts from the storage device to these I/O cores. This implementation can avoid interrupts on VM cores and, to some extent, improve cache hit rates.

#### V. EXPERIMENTAL METHODOLOGY

To validate the prototype of our design, we deployed it into the POWER8 platform, the prototype system was based on Linux Kernel 3.19 and QEMU 2.3.1. In this section, we introduce our measurement environment and test cases of the profiling. We look at intensive block I/O workloads by using FIO, and consider both throughput and latency.

## *A. Platform Setup*

The Power S822L (8247-22L) server is a powerful 2-socket server that ships with 20 fully activated cores (10 cores per socket) and I/O configuration flexibility to meet today's growth and tomorrow's processing needs [21]. The system includes 192GB of memory, the null block device and a Samsung SM1715 1.6TB NVM-Express soild state drive (SSD) [22] with the Nallatech 385 CAPI card. For scalability-minded evaluation, the VM running on the platform has 10 vCPUs and 64GB RAM, and each vCPU is mapped to a physical core of socket #1.

Note that two types of storage devices were used in our measurement. The null block device use memory to mimic a virtual high performance storage device with parallel data design. The null block device can validate a higher range of performance where the real storage device cannot reach. In the meanwhile, we utilized a Samsung SM1715 1.6TB NVM-Express SSD to enlarge our evaluation scope. The NVM-Express is a logical device interface specification for accessing non-volatile storage media via PCI-Express (PCIe) bus. It allows levels of parallelism found in modern SSDs to be fully utilized by the host hardware and software. It is able to handle storage data in parallel on a multi-core system without synchronizations among each core because it has 2048 MSI-X interrupts and 65,536 queues that each of them has 65,536 commands. Furthermore, the paired submission and completion queue mechanism is used for efficient and improve performance with minimal latency.

### *B. I/O Workload Generation and Trace Collection*

We focused our profiling on throughput and latency. We measured throughput by overlapping the submission of asynchronous I/O requests. The I/O workloads for measurements are generated by FIO. FIO is widely used by research fellows to validate their work [3], [18], [23]. It is able to carefully control several kinds of configurations like block device, block size, queue-depth, I/O engine, cache mode and the number of I/O processes. Moreover, there are many detailed information such as the number of context switch, throughput, IOPS and latency. These outputs are very helpful for us to analyze the results. In our measurements, each workload ran for 60 seconds in order to collect sufficient data.

We also used an efficient Linux kernel trace tool (*ftrace*) to trace the I/O activities at the block layer. The trace data were stored in the *tmpfs* which is a temporary filesystem that resides in memory in order to minimize the interference caused by tracing.

![](_page_5_Figure_8.png)

Fig. 4. To verify effiectiveness of multiple virtual queues inside the *virtio* paravirtual driver by using FIO test cases (4KB, random read, direct I/O, 32 iodepth, libaio and jobs=N). After comparison, both scalability and performance got a lot improvement when the number of *virtqueues* is increased, but the improved IOPS is no more than the result of the same FIO workload running in the host.

![](_page_5_Figure_10.png)

Fig. 5. To verify effectiveness of multiple I/O threads by using FIO test cases (4KB, random read, direct I/O, 32 iodepth, libaio and jobs=N). Notice that both scalability and performance have a prominent improvement by using multiple I/O threads to handle I/O requests together. In particular, when the number of I/O threads is equal to the number of *virtqueues*, the I/O performance reaches peak value.

## *C. Performance Metrics*

The primary metrics of our experiments were absolute throughput (IOPS) and latency (-seconds) of the block layer. We contrasted the results between virtualization and baremetal system, and proved that the former can approach the latter.

## VI. EVALUATION

In this section, we present performance evaluation results. The evaluation has two phases:

In the first phase of evaluation, we performed measurements on the prototype system to test the effects of 4 parts, including multiple virtual queues, dedicated host I/O threads, switch-less notification mechanism and the I/O affinity configuration. In this phase, the measurements were taken on the null block device.

![](_page_6_Figure_0.png)

Fig. 6. Verifications on three notification mechanisms and cases of their optimization on I/O affinity. The comparison test was performed by running FIO test cases (libaio, randread, direct I/O, iodepth=32, bs=4K, jobs=N). In the case of miltiple I/O intensive workloads, the measured values of *polling* mechanism is increased by up to 10.6% on average compared to the native. On an average, the measured values of *polling* is approximately 5.8% lower than the *guest to host IPI* case. In addition, all of three notification mechanisms get an extra boost by taking advantage of I/O affinity configuration, the improved performance is approximately 4.5%.

In the second phase of evaluation, we compared our design, *virtio-blk-data-plane* and bare-metal system. The *virtio-blkdata-plane* technique is a current state-of-the-art paravirtual I/O technique for the KVM which improves the block I/O performance by using a single dedicated I/O thread which avoids the QEMU global mutex for each storage devices. In this phase, the measurements were taken on the null block device and the real NVMe SSD respectively.

In the remaining of the paper, we denote the *virtio-blkdata-plane* as *Baseline*, donate our design as HPSVSIO (High Performance and Scalable Virtual Machine Storage I/O), and denote bare-metal system as *Bare-metal*.

### *A. Impact of Multiple Virtual Queues*

For verifying the improvement by introducing multiple *virtqueues* into one *virtio-blk* device, we did not use multiple dedicated I/O threads for these virtual queues. Instead, only one host I/O thread was still kept in this virtual device I/O thread context as same as the *Baseline*. The number of *virtqueues* in the *front-end* driver was increased from 1 to 4, and due to the guest OS was a Linux distribution, therefore each virtual queue was mapped to *blk-mq*'s hardware dispatch queue in the guest OS's block layer. We used FIO test cases (libaio, randread, direct I/O, iodepth=32, bs=4K, jobs=N) running in the guest OS to verify the improvement, because performance specifications on a storage system are often the result of a synthetic test using the most favorable block size (often 4K or smaller) to maximize the number of IOPS [24].

Figure 4 shows that there is an obvious growth in IOPS by increasing the number of *virtqueues*. In this comparison, both scalability and performance got a lot improvement when the number of *virtqueues* is increased, but the improved IOPS is no more than the result of the same FIO test case running in the host.

We found that two major reasons lead to this limited improvement. On the positive aspect, it is benefit from the architecture of *blk-mq*. Note that the block layer of the current Linux Kernel is *blk-mq*. With *blk-mq* in multicore environment, the number of software staging queues is typically the same as the number of cores. Therefore, providing multiple hardware dispatch queues may enhance parallel effect. In our tests, the multiple *virtqueues* were mapped to *blk-mq*'s hardware dispatch queues, so that the throughput was improved due to improve the guest OS's block I/O parallelism. However, the negative is that only one I/O thread handles requests from all these queues, the overall throughput of the guest OS is very close to the result of the same FIO test case running in the host. In all, more host I/O thread should be used for handling I/O requests from multiple *virtqueues* to get more scalability and performance improvement.

#### *B. Impact of Multiple I/O Threads*

After verifying the effect of multiple queues, we look at the impact of multiple I/O threads. We also employed FIO test cases (libaio, randread, direct I/O, iodepth=32, bs=4K, jobs=N) running in the guest OS to explore the effectiveness of the multiple I/O threads. The number of *virtqueues* was set to 4, and the number of I/O threads was increased from 1 to 4. To ensure the parallelism among every I/O thread, we specified CPU affinity for each I/O thread to prevent some of them from a long time waiting for scheduling. Therefore, I/O requests in multiple *virtqueues* were handled in parallel. However, the notification mechanism used in this part was the native way of event-driven. Therefore, costs of context switch is required for each notification.

Figure 5 shows that both scalability and performance have a prominent improvement by using multiple I/O threads to handle I/O requests, particularly when the number of I/O threads is equal to the number of *virtqueues*.

## *C. Impact of Switch-less notifications and I/O Affinity*

The multiple I/O threads seems to solve the parallel issue of block I/O in virtualization. After measurement, we found that there still existed about 40 percent performance degradation caused by the complex I/O path. In our point of view, the native notification mechanism may cause lots of context switches, especially in the case of multiple I/O threads. So the switch-less notification mechanism and I/O affinity configuration were presented by us to ease this costs.

As we described previously, two types of switch-less notification mechanisms are introduced: *guest to host IPI* and *polling*. The *guest to host IPI* is POWER8 architecture specific, while the polling can be deployed in various architecture. We implemented both of them in our POWER8 server, and verified their effectiveness. We compared *guest to host* IPI, *polling* and the native notification based on *exit*. The comparison test was performed by running FIO test cases (libaio, randread, direct I/O, iodepth=32, bs=4K, jobs=N) in three systems with different notification mechanism mentioned above.

As shown in Figure 6, it is clearly that the performance of two switch-less notification mechanisms were better than that of the native. In the case of miltiple I/O intensive workloads, the measured values of *polling* mechanism is increased by up to 10.6% on average compared to the native. On an average, the measured values of *polling* is approximately 5.8% lower than the *guest to host IPI* case. Generally, it is observed that *guest to host IPI* case is more efficient benefit from POWER8 architecture features. In addition, all of three notification mechanisms get an extra boost by taking advantage of I/O affinity configuration, the improved performance is approximately 4.5%. Mostly because I/O threads benefit from dedicated cores, all I/O threads can handle I/O requests and completions as soon as possible without unnecessary CPU scheduling.

Here, we want to pay more attention to switch-less notification based on *polling* due to it may be deployed in different architecture. The advantage of using the polling mechanism is that it can indeed be able to ease the interrupt overhead and remove the context switch costs. By tracing the block I/O workflow, a 4KB direct I/O read, the polling mechanism reduce the latency per request from 40s to 13.5s. However, it is important to note that the key concern for switch-less notification based on *polling* is the impact on the CPU usage rate. From the comparison result showed in Figure 6, we found that the effectiveness of the *polling* mechanism was changing along with the usage rate of CPU. When the number of parallel processes is small, the performance of the switchless notification mechanism based on *polling* is nearly the same as the *guest to host IPI* case. While when the number of parallel processes comes to larger, the advantage of the *polling* mechanism is not obvious compared to the native. Because each *polling* thread has to wait for a long time until it is scheduled.

After finishing the analysis in the first phase evaluation,

![](_page_7_Figure_6.png)

Fig. 7. Performance evaluation on *read* and *write* I/O workloads among Baseline, prototype and bare-metal using a Null Block Device.

the configuration of the prototype system used in the second phase evaluation was as follows: 10 multiple *virtqueues*, 10 dedicated I/O threads, the switch-less notification mechanism based on *guest to host IPI* and I/O affinity.

#### *D. Evaluation on Null Block Device*

We used the null block device to mimic a high performance *blk-mq*-based storage device, and evaluated performance of three targets, as shown in Figure 7. The I/O intensive workloads were generated by FIO. There were 2 types of I/O workloads (libaio, randread/randwrite, direct I/O, iodepth=32, bs=4K, jobs=N), and we varied the number of workloads from 1 to 10 in the measurement. Figure 7(a) illustrates the random read case. It is obvious that Bare-metal performs striking throughput arriving 3 million IOPS which the maximum performance can be measured on our test platform. The throughput of Baseline drops gradually as the number of workloads increased. The throughput of the prototype goes up as quickly as Bare-metal. When executing 10 workloads in parallel, The prototype's throughput is 40X than Baseline, and no more than 32% performance degradation compared to Baremetal. Figure 7(b) depicts the results of block I/O latency in the evaluation. The latency of Baseline is the longest, and rises gradually as the number of workloads increases. The latency of the prototype is slightly longer than that of Bare-metal, and there is no significant increase by varying the number of parallel workloads. The results of the random write case are

![](_page_8_Figure_0.png)

![](_page_8_Figure_1.png)

![](_page_8_Figure_2.png)

Fig. 8. Performance comparison on *read* and *write* I/O-intensive workloads among Baseline, prototype and bare-metal using an NVMe-based SSD

as similar as the random read case, as shown in Figure 7(c), 7(d).

The results shown in Figure 7 indicates that the prototype is able to process block I/O workloads in parallel. However, the performance gap between the VM and the bare-metal is not filled completely. It is not mean that our design has defects, this is because the block I/O path in virtualization is longer and more complex than that of bare-metal. This overhead is too difficult to be eliminated.

#### *E. Evaluation on NVM-Express Device*

50K

In the end of our evaluation, we performed the same evaluation by using a real physical high performance storage device in order to enlarge the evaluation scope.

Firstly, we measured performance of the SM1715 NVM-Express SSD in the bare-metal system to survey its maximum throughput. Compared to the null block device, the real storage device has relatively poor throughput which is limited to 750K random read IOPS and 130K random write IOPS. As shown in Figure 8(a), 8(c), the throughput improvement is stopped when 8 parallel I/O-intensive workloads is executed in parallel, and there is no obvious increase of throughput when the number of parallel workloads increases from 8 to 10. the performance of Baseline also drops as the number of parallel workloads increases. But the performance of prototype almost reaches the performance cap of the SM1715 when the number of parallel workloads comes to 10, the performance slowdown is not be more pronounced in this case.

Therefore, based on the results shown in Figure 8, we can conclude that the prototype can make full use of the underlying high performance storage device.

#### VII. RELATED WORK

As the hypervisor playground, Linux offers a variety kinds of hypervisor solutions with different advantages and attributes. However, the narrow I/O path, mutex contention and frequent context switch (*exit* and *entry*) have dramatically decreased the I/O performance in virtualized environment [14], [25]. Consequently, most recent studies have concentrated on eliminating overheads of virtualization in block I/O. The effective approaches can be divided into two main categories: hardware acceleration and software optimization.

Numerous manufacturers provide a number of interfaces and technologies for supporting I/O virtualization at the hardware layer like SR-IOV (Single Root I/O Virtualization) [26], IOMMU (I/O Memory Management Unit) [27], [28], [29], Intel VT-d [30], [31] and Steata Storage System [32]. These outstanding methods present superior quality when adopting them into virtualization infrastructure, even the performance is close to that of bare-metal environment, but they could be inappropriate in some condition since they are lack of compatibility to all architectures and expensive specialized hardware is a need. Moreover, some of these hardware ways such as SR-IOV and IOMMU require a dedicated VM (Virtual Machine) to comply with an underlying physical device that leads limitation to the benefits of virtualization like VMs Live migration [33], [34]. Therefore, many subsequent efforts still remain to be done to overcome the limitations of the hardware approaches.

In the meanwhile, several studies have surveyed the issues of I/O overheads triggered during communications between the VM and the hypervisor. They have devised some softwarebased ways such as *virtio* paravirtualized framework, Efficient and Scalable Para-virtual I/O System (ELVIS) [15] and ELI (Exit-Less Interrupts) [35] in order to decrease the I/O overheads in virtualization. These methods provide more or less performance improvement by optimizing the block I/O path and relieving mutex contention in virtualized environment. However, they do not solve the performance degradation when using the multiqueue high-performance storage device in virtualization, and that is what we are most concerned about.

#### VIII. CONCLUSION

In this paper, we discuss the shortage of the current block I/O layer in virtualization, which is unable to handle the block I/O requests in parallel. Therefore, we propose a multithreaded block I/O layer to solve this problem. This design make use of multiple virtual queues and multiple I/O threads to alleviate the I/O contention so as to improve the performance. In the meanwhile, we provide switch-less notification mechanism and I/O affinity optimization in order to provide further performance optimization. We implement a prototype based on the KVM hypervisor and perform a detailed evaluation to verify its effectiveness. The results evidence the superiority of our design and its well scalability in multi-core environment.

In addition, we commit patches generated from our implementation to the Linux community and some of them have been already merged into the mainline Linux kernel. These patches bring significant block I/O performance improvement for virtualization in the real system.

## ACKNOWLEDGEMENT

This work was supported by the National Science Foundation of China grants No.61321491, and in part by Commission of Economy and Information Technology grants the project of the security protection foundation of operating system based on hardware resource isolation mechanism.

#### REFERENCES

- [1] Danny Cobb and Amber Huffman. Nvm express and the pci express ssd revolution. In *Intel Developer Forum, San Francisco, CA, USA*, 2012.
- [2] Angelos Bilas. Scaling i/o in virtualized multicore servers: How much i/o in 10 years and how to get there. In *Proceedings of the 6th international workshop on Virtualization Technologies in Distributed Computing Date*, pages 1–2. ACM, 2012.
- [3] Matias Bjørling, Jens Axboe, David Nellans, and Philippe Bonnet. Linux block io: introducing multi-queue ssd access on multi-core systems. In *Proceedings of the 6th International Systems and Storage Conference*, page 22. ACM, 2013.
- [4] Rusty Russell. virtio: towards a de-facto standard for virtual i/o devices. *ACM SIGOPS Operating Systems Review*, 42(5):95–103, 2008.
- [5] Paul Barham, Boris Dragovic, Keir Fraser, Steven Hand, Tim Harris, Alex Ho, Rolf Neugebauer, Ian Pratt, and Andrew Warfield. Xen and the art of virtualization. In *ACM SIGOPS Operating Systems Review*, volume 37, pages 164–177. ACM, 2003.
- [6] Hiroshi Tezuka, Francis O'Carroll, Atsushi Hori, and Yutaka Ishikawa. Pin-down cache: A virtual memory management technique for zero-copy communication. In *Parallel Processing Symposium, 1998. IPPS/SPDP 1998. Proceedings of the First Merged International... and Symposium on Parallel and Distributed Processing 1998*, pages 308–314. IEEE, 1998.
- [7] Sanjay Kumar, Himanshu Raj, Karsten Schwan, and Ivan Ganev. Rearchitecting vmms for multicore systems: The sidecore approach. In *Workshop on Interaction between Opearting Systems & Computer Architecture (WIOSCA)*. Citeseer, 2007.
- [8] Guangdeng Liao, Danhua Guo, Laxmi Bhuyan, and Steve R King. Software techniques to improve virtualized i/o performance on multicore systems. In *Proceedings of the 4th ACM/IEEE Symposium on Architectures for Networking and Communications Systems*, pages 161– 170. ACM, 2008.
- [9] Jiuxing Liu and Bulent Abali. Virtualization polling engine (vpe): using dedicated cpu cores to accelerate i/o virtualization. In *Proceedings of the 23rd international conference on Supercomputing*, pages 225–234. ACM, 2009.
- [10] Lamia Youseff, Rich Wolski, Brent Gorda, and Chandra Krintz. Paravirtualization for hpc systems. In *Frontiers of High Performance Computing and Networking–ISPA 2006 Workshops*, pages 474–486. Springer, 2006.
- [11] Amber Huffman. Nvm express, revision 1.0 c. *Intel Corporation*, 2012.
- [12] Abel Gordon, Nadav Har'El, Alex Landau, Muli Ben-Yehuda, and Avishay Traeger. Towards exitless and efficient paravirtual i/o. In *Proceedings of the 5th Annual International Systems and Storage Conference*, page 10. ACM, 2012.
- [13] Alex Landau, Muli Ben-Yehuda, and Abel Gordon. Splitx: Split guest/hypervisor execution on multi-core. In *WIOV*, 2011.
- [14] Keith Adams and Ole Agesen. A comparison of software and hardware techniques for x86 virtualization. *ACM Sigplan Notices*, 41(11):2–13, 2006.
- [15] Nadav Har'El, Abel Gordon, Alex Landau, Muli Ben-Yehuda, Avishay Traeger, and Razya Ladelsky. Efficient and scalable paravirtual i/o system. In *USENIX Annual Technical Conference*, volume 26, pages 231–242, 2013.

- [16] Olivier Maquelin, Guang R Gao, Herbert HJ Hum, Kevin B Theobald, and Xin-Min Tian. Polling watchdog: Combining polling and interrupts for efficient message handling. In *ACM SIGARCH Computer Architecture News*, volume 24, pages 179–188. ACM, 1996.
- [17] Constantinos Dovrolis, Brad Thayer, and Parameswaran Ramanathan. Hip: hybrid interrupt-polling for the network interface. *ACM SIGOPS Operating Systems Review*, 35(4):50–60, 2001.
- [18] Muli Ben-Yehuda, Michael Factor, Eran Rom, Avishay Traeger, Eran Borovik, and Ben-Ami Yassour. Adding advanced storage controller functionality via low-overhead virtualization. In *FAST*, volume 12, pages 15–15, 2012.
- [19] R Russell, MS Tsirkin, C Huck, and P Moll. Virtual i/o device (virtio) version 1.0. *OASIS Standard, OASIS Committee Specification*, 2, 2015.
- [20] Alberto Martinez, James Chapple, Prashant Sethi, and Joseph Bennett. Circuitry to selectively produce msi signals, June 29 2004. US Patent App. 10/881,076.
- [21] Balaram Sinharoy, JA Van Norstrand, Richard J Eickemeyer, Hung Q Le, Jens Leenstra, Dung Q Nguyen, B Konigsburg, K Ward, MD Brown, Jose E Moreira, et al. Ibm power8 processor core microarchitecture. ´ IBM *Journal of Research and Development*, 59(1):2–1, 2015.
- [22] Ji Jun Hung, Kai Bu, Zhao Lin Sun, Jie Tao Diao, and Jian Bin Liu. Pci express-based nvme solid state disk. In *Applied Mechanics and Materials*, volume 464, pages 365–368. Trans Tech Publ, 2014.
- [23] Woong Shin, Qichen Chen, Myoungwon Oh, Hyeonsang Eom, and Heon Y Yeom. Os i/o path optimizations for flash solid-state drives. In *USENIX Annual Technical Conference*, pages 483–488, 2014.
- [24] Pete Koehler. Understanding block sizes in a virtualized environment. https://vmpete.com/2016/03/03/ understanding-block-sizes-in-a-virtualized-environment/. Accessed March 3, 2016.
- [25] Muli Ben-Yehuda, Michael D Day, Zvi Dubitzky, Michael Factor, Nadav Har'El, Abel Gordon, Anthony Liguori, Orit Wasserman, and Ben-Ami Yassour. The turtles project: Design and implementation of nested virtualization. In *OSDI*, volume 10, pages 423–436, 2010.
- [26] Author Unknown. Single root i/o virtualization and sharing specification, revision 1.0. Sep, 11:1–84, 2007.
- [27] Muli Ben-Yehuda, Jon Mason, Jimi Xenidis, Orran Krieger, Leendert Van Doorn, Jun Nakajima, Asit Mallick, and Elsie Wahlig. Utilizing iommus for virtualization in linux and xen. In *OLS06: The 2006 Ottawa Linux Symposium*, pages 71–86. Citeseer, 2006.
- [28] I AMD. O virtualization technology (iommu) specification. *AMD Pub*, 34434, 2007.
- [29] Muli Ben-Yehuda, Jimi Xenidis, Michal Ostrowski, Karl Rister, Alexis Bruemmer, and Leendert Van Doorn. The price of safety: Evaluating iommu performance. In *The Ottawa Linux Symposium*, pages 9–20, 2007.
- [30] R Hiremane. Intel virtualization technology for directed i/o (intel vt-d). *Technology@ Intel Magazine*, 4(10), 2007.
- [31] Jianhua Che, Qinming He, Qinghua Gao, and Dawei Huang. Performance measuring and comparing of virtual machine monitors. In *Embedded and Ubiquitous Computing, 2008. EUC'08. IEEE/IFIP International Conference on*, volume 2, pages 381–386. IEEE, 2008.
- [32] Brendan Cully, Jake Wires, Dutch Meyer, Kevin Jamieson, Keir Fraser, Tim Deegan, Daniel Stodden, Geoffre Lefebvre, Daniel Ferstay, and Andrew Warfield. Strata: High-performance scalable storage on virtualized non-volatile memory. In *Proceedings of the 12th USENIX Conference on File and Storage Technologies (FAST 14)*, pages 17–31, 2014.
- [33] Christopher Clark, Keir Fraser, Steven Hand, Jacob Gorm Hansen, Eric Jul, Christian Limpach, Ian Pratt, and Andrew Warfield. Live migration of virtual machines. In *Proceedings of the 2nd conference on Symposium on Networked Systems Design & Implementation-Volume 2*, pages 273– 286. USENIX Association, 2005.
- [34] Uri Lublin and Qumranet Anthony Liguori. Kvm live migration. In *KVM Forum*, 2007.
- [35] Abel Gordon, Nadav Amit, Nadav Har'El, Muli Ben-Yehuda, Alex Landau, Assaf Schuster, and Dan Tsafrir. Eli: bare-metal performance for i/o virtualization. *ACM SIGPLAN Notices*, 47(4):411–422, 2012.

