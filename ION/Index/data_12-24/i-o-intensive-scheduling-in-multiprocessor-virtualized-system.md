# I/O-intensive Scheduling in Multiprocessor Virtualized System

Haoxiang Mao Department of Computer Science and Engineering Shanghai Jiao Tong University Shanghai 200240, P.R. China maohaoxiangI23@sjtu.edu.cn

Abstract-Virtualization is becoming an important part of cloud computing and high performance calculation. In the virtualized system, the scheduler plays an important role in effecting the performance of whole system. Traditional scheduler that focus on the fairness of VMs would cause problems in I/O performance and latency. In order to eliminate the 1/0 latency issue, we propose a virtual machine scheduling model based on multiprocessor system. We also implement a prototype in Xen 4.3.0 and evaluate it with several benchmarks. Experiment results demonstrate that our scheduling model can improve the I/O performance effectively. The bandwidth of disk increase by 53.6% and that of network increase by 39.4%. Meanwhile, our method does not change the scheduling algorithm of CPUintensive VM so that the scheduling fairness is ensured.

#### Keywords-Virtualization; 110; scheduling; Xen;

## I. INTRODUCTION

High performance calculating and cloud computing are becoming more and more popular, which cause virtualization becoming an important role in modern life [ 1]. For example, commercial cloud providers such as Amazon EC2 [2] use virtualization to allocate different types of virtual machines on the same hardware platform for customers to meet their different demands. Virtualization technology provides the improvement of resource utilization, application portability and efficiency of system management [3].

However, there are several challenges remaining to be addressed when using virtualization in high performance computing (HPC) platform. One of them is the 110 latency issue. Generally, the 110 operations such as disk and network requests are very important in the HPC platform. In nonvirtualized environment, the OS has infonnation of all tasks so that the 110 tasks can preempt other CPU tasks to achieve a better performance [4] [5] [6]. While in virtualized environment, traditional virtual machine scheduler focus on the fairness of CPU time between domains, which makes 110 resources less important. Thus, the latency of IIO-bound applications will become longer than in non-virtualized environment.

When it comes to the cloud environment, the latency problem becomes even worse. In the cloud environment,

Bindi Huang Department of Computer Science and Engineering Shanghai Jiao Tong University Shanghai 200240, P.R. China huangbindi@sjtu.edu.cn

different users often apply for virtual machines to run different types of applications. Some of them are CPU-bound and others are I/O-bound. The customers may desire a fast response for IIO-bound VM, but they may desire a well calculation ability for CPU-bound VM. Since there are many VMs in many physical cores, when more than one VMs run in one same physical core, a VM with 110 requests has to wait for its turn to access CPU for processing the requests. The latency is supposed to be a multiple of default scheduling time slice (e.g. 30ms in Xen). This is harmful for IIO-bound applications.

To avoid these problems, one could pin only one VM to a physical core and this can eliminate competition forever. However, that would increase the cost which is not desired by the customers. There are also many other researches on how to improve the virtualized 110 perfonnance. Hwanju Kim et al. proposed a task-aware virtual machine scheduling mechanism using gray-box knowledge [ 13]. And Govindan et al. proposed a communication-aware VM scheduling mechanism in consolidated hosting environment [ 14].

In this paper, we propose our solution named iSche to reduce 110 latency in multiprocessor virtualized system. We analyze and address the problem of 110 latency in Xen credit scheduler. We design and implement a prototype of virtual machine scheduler based on mUltiprocessor system in Xen 4.3.0. And our evaluation shows that the performance of 110 bound VMs has been improved. We improve the bandwidth of disk 54.6% and the throughput of network 39.4%.

The rest of this paper is organized as follows. We discuss the background in Section II. Then Section III presents the design and implementation of iSche. Section IV gives the details of evaluation. And we conclude our work in the last section.

# II. BACKGROUND

In this section, we first introduce the Xen credit scheduler. Then we discuss the problems by a simple experiment.

#### A. The Xen Credit Scheduler

Xen [7] is an open source virtual machine monitor (VMM). In Xen, domainO (the host) runs the control software and the backend drivers while domainU (the guest) runs users applications. Xen has three schedulers, including Borrowed Virtual Time (BVT) scheduler, Simple Earliest Deadline First (SEDF) scheduler and the Credit scheduler. BVT is usually used for some delay-sensitive tasks [8]. SEDF is suitable for real-time tasks [9]. The default scheduler in Xen is the Credit scheduler [ 10].

The credit scheduler is a fair share CPU scheduler as the default scheduler of Xen on SMP hosts. Each domain (including the host OS) is assigned a weight and a cap. A domain with more weight gets more CPU time on a contended host. The cap limits the maximum amount of CPU time that a domain will be able to consume. When cap is set, a domain must wait for next schedule period if it consumes up all its credit even if the host system has no other domains to run.

Each physical CPU manages a run queue of runnable VCPUs. This queue is sorted by VCPUs' priority. A VCPU's priority can be OVER or UNDER, which represent whether this VCPU has exceeded its fair share of CPU resource or not. When the scheduler insert a VCPU into a run queue, it put the VCPU after all other VCPUs which have the equal priority. When a VCPU runs, it consumes credits. Negative credits imply a priority of over. A VCPU's priority becomes under if it consumes all its allocated credits. At every scheduling decision, the next VCPU to run is picked off the head of the run queue by the scheduler. When a CPU doesn't fmd a VCPU whose priority is UNDER on its local run queue, it comes to other CPUs to pick one. This is the load balance which guarantees each VM receives its fair share of CPU resources systemwidely [ 10].

# B. Problems of 1/0 Processing Latency

In Xen (as well as other VMM such as KVM [11], VMware [ 12]), 1/0 requests are first delivered to domainO and then the domainO forwards them to the target VM. The target VM could process the request and send a response at the next time it is scheduled. Since the scheduling policy of credit is round robin, here we comes some problems. For instance, suppose we have 4 VMs in one physical core, as shown in Fig. 1.

When VMI has consumed all its credit, the scheduler selects VM2 to run. When an I/O request comes for VMI, it has to be buffered until VMl is rescheduled. Suppose we use 30ms as the default time slice, VMI must wait for 90ms (e.g. 3*30ms) to process its requests. Therefore, the I/O latency can be reached as high as 90ms in the worst case. In fact, the worst waiting time could be even longer.

![](_page_1_Figure_6.png)

Fig I. Scheduling latency in Xen

![](_page_1_Figure_8.png)

Fig 2. CDF of ping round-trip time

We perform a simple experiment to demonstrate this problem. We vary the number of VMs sharing one physical CPU from 2 to 4, each VM run CPU loop, and calculate the CDF of the round-trip time (RTT) of VMl. The result is shown in Fig. 2. Our results show that the ping RTT increases with the number of VMs in one core. And the worst RTT in 4VMs is as much as two times of that in 2VMs.

#### III. DESIGN AND IMPLEMENT A TION

In this section, we present our design and implementation of iSche. Subsection A presents the architecture of our system, subsection B and C discuss the details of implementation.

## A. Design of the Scheduling Model

In virtualized environment, the requirements for CPU resource of domainUs are different when they run different applications. CPU-intensive VMs generally run continuously and consume up all its credit. On the contrary, I/O-intensive VMs need less CPU time. What they need are high-rate scheduling switch, so that they can process I/O requests in time. On the one-processor system, all of VMs are running in the same core to share CPU time. I/O-intensive VMs are treated the same with the CPU-intensive ones. So the I/O-intensive VMs have to wait for their tum to handle the I/O requests. And it's hard to apply different scheduling strategy to only one processor. When it comes to multiprocessor system, we can apply different strategies into different processors.

In our system, we define two types of cores, General Core and I/O core. The general core is used to run domainO and CPU-intensive VMs. While the I/O core is used for I/Ointensive VMs to improve the performance. We use different strategies on different types of cores. The general cores use the credit scheduling algorithm of Xen to fairly schedule all the CPU-intensive VMs. The I/O cores switch VMs more frequently to provide more opportunities for I/O-intensive VMs to process I/O requests. The architecture of our system is shown in Fig. 3.

As shown in Fig. 3, one model is added into VMM. The scheduling decision model is mainly used to collect all the information of domainUs and schedule them in a suitable core.

![](_page_2_Figure_0.png)

![](_page_2_Figure_1.png)

At first, this model separate general cores and 110 cores according to the admin's strategy. Then we pin domainO to a general core because it's the host and we can always treat it as a CPU-intensive VM. Thirdly, it monitor the type of all the domainUs and pin IIO-intensive VMs to I/O cores and CPUintensive VMs to general cores. The algorithm in the 110 cores is different from that in general cores so we can treat 1/0 intensive VMs differently.

## B. Implementation of Scheduling Decision Model

As mentioned above, first thing the model should do is to separate general cores and 110 cores. We provide an interface to the administrative tools (such as xl in Xen) to configure the number of each core. Then this model randomly pick several cores and label them as general cores, and label others as 110 cores. Whenever the administrator change the configure file, this model relabels all the cores.

The scheduling decision model needs to distinguish 1/0 intensive VMs from CPU-intensive VMs. We left the decision on whether a particular VM is IIO-intensive or CPU-intensive to the administrator. And the xl tools is provided. The decision model maintains a list of all the IIO-intensive VMs and CPUintensive VMs. When the type of a VM is changed, it can easily change the list the VM belongs to. The algorithm of 110 cores is changed so that when picking next VM to run, 110 cores will pick VMs from the 110 list instead of all the VMs.

#### C. Time Slice of 1/0 Core

We use 10ms as the default time slice in 110 cores (the default time slice in Xen is 30ms). Consequently, the switch frequency of I/O-intensive can be three times more than before.

# IV. EVALUATION

We perform several experiments to evaluate our system. We evaluate both disk 110 performance and network 110 performance of iSche. And we discuss the improvement made by our system.

![](_page_2_Figure_10.png)

Fig 4. Test result of disk bandwidth

## A. Experiment Setup

The hardware configuration of our experiment is as follows: Intel Core i5-3450 quad-core CPU, 16GB memory, 100Mbps Ethernet NIC, lTB SATA disk. Our system runs Xen 4.3.0 as virtual machine monitor. We use Ubuntu 13.04 as the operating system of the domainO and all domainUs. The version of the Linux distribution is Linux-3.8.0 kernel.

#### B. Evaluation with Disk 1/0

To evaluate the performance of disk 110, we run 4 VMs concurrently. Three of them are CPU-intensive and one is 110 intensive which is the one to be evaluated. Here we denote it as domainl. We fustly run CPU-bound application (here is the CPU loop) in all four VMs, and then use the dd command in domain 1 to test the bandwidth of the disk. We use dd to read and write 2GB data with 64kB block size. The bandwidth test result is shown in Fig. 4.

As shown in Fig. 4, the average disk bandwidth is about

![](_page_2_Figure_17.png)

Fig 5. Test result of network throughput

![](_page_3_Figure_0.png)

50MB/s in default case. The iSche improves the average bandwidth from 64.45MB/s to 99.01MB/s. The increasing rate is nearly 53.6%.

#### C Evaluation with Network 1/0

To evaluate the performance of network 110, we run 4 VMs concurrently. The case situation is the same as evaluation with disk 110. We first run the netperf [ 15] to evaluate the throughput of network 110. We evaluate the TCP _STREAM between iSche and default Xen. As shown in Fig. 5, the iSche improves the average throughput from 66. 77Mb/s to 93.1 1Mb/s with the increasing rate of 39.4%.

Next we test the ping latency comparing with default Xen credit scheduler. As shown in Fig. 6, we can find that the RTT of iSche is less than default one. This is because the 110 intensive VM is scheduled more frequently. So when network 110 events come, VM can handle these very quickly and thus reduces the latency caused by the scheduling delay.

#### CONCLUSION

We have presented iSche to pin different types of VM to different types of cores. OUf system can reduce the latency of IIO-intensive VMs without much effect on the performance of CPU-intensive VMs. We increase the switch frequency of 110 intensive VM to process more 110 requests. Our evaluation of a

# Xen-based prototype demonstrates improvement at both disk 110 and network 110.

## REFERENCES

- [I] L. M. Vaquero, L. Rodero-Merino, J. Caceres, and M. Lindner, "A break in the clouds: towards a cloud definition," SIGCOMM Comput. Commun. Rev., vol. 39, no. I, pp. 50-55, Dec. 2008.
- [2] http://aws.amazon.com/ec2.
- [3] Y. Hu, X. Long, J. Zhang, 1. He, and L. Xia, "1/0 scheduling model of virtual machine based on multi-core dynamic partitioning," in Proceedings of the 19th ACM International Symposium on High Performance Distributed Computing. ACM, 2010, pp. 142-154.
- [4] D. Bovet and M. Cesati, Understanding The Linux Kernel. Oreilly & Associates Inc, 2005.
- [5] M. K. McKusick and G. V. Neville-Neil, "Thread scheduling in freebsd 5.2," Queue, vol. 2, no. 7, pp. 58-64, Oct. 2004. [Online]. Available: http://doi.acm.org/10.1145/1 035594.1 035622
- [6] M. E. Russinovich and D. A. Solomon, Microsoft Windows Internals, Fourth Edition: Microsoft Windows Server(TM) 2003, Windows XP, and Windows 2000 (Pro-Developer). Redmond,WA, USA: Microsoft Press, 2004.
- [7] P. Barham, B. Dragovic, K. Fraser, S. Hand, T. Harris, A. Ho, R. Neugebauer, 1. Pratt, and A. Warfield, "Xen and the art of virtualization," in Proceedings of the nineteenth ACM symposium on Operating systems principles, ser. SOSP '03. New York, NY, USA: ACM, 2003, pp. I64-In
- [8] K. 1. Duda and D. R. Cheriton. Borrowed-virtual-time (BVT) Scheduling: Supporting Latency-sensitive Threads in a General-purpose Scheduler. SIGOPS Oper. Syst. Rev., 33(5):261-276, 1999.
- [9] 1. M. Leslie, D. Mcauley, R. Black, T. Roscoe, P. T. Barham, D. Evers, R. Fairbairns, and E. Hyden. The Design and Implementation of an Operating System to Support Distributed Multimedia Applications IEEE Journal of Selected Areas in Communications, 14(7), 1996.
- [10] http://wiki.xen.org/wiki/Credit Scheduler.
- [11] A. Kivity, "kvm: the Linux virtual machine monitor," in OLS '07: The 2007 Ottawa Linux Symposium, Jul. 2007, pp. 225-230.
- [12] C. A. Waldspurger, "Memory resource management in vmware esx server," in Proceedings of the 5th symposium on Operating systems design and implementation, ser. OSDI '02. USENIX, 2002, pp. 181- 194.
- [13] H. Kim, H. Lim, J. Jeong, H. Jo, and 1. Lee. Task-aware Virtual Machine Scheduling for 1/0 Performance. In Proceedings of the 5th ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'09), pages 101-110, New York, NY, USA, Mar. 2009. ACM.
- [14] S. Govindan, A. R. Nath, A. Das, B. Urgaonkar, and A. Sivasubramaniam. Xen and Co.: Communication-aware CPU Scheduling for Consolidated Xen-based Hosting Platforms. In Proceedings of the 3th ACM SIGPLAN/SIGOPS International Conference on Virtual Execution Environments (VEE'07), pages 126- 136, New York, NY, USA, June 2007. ACM.
- [15] http://www.netperf.org/netperf/.

