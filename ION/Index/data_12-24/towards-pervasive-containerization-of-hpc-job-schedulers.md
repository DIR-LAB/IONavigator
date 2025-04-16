# Towards pervasive containerization of HPC job schedulers

Christophe Cerin ´ *LIPN UMR CNRS 7030 University Sorbonne Paris Nord* Villetaneuse, France christophe.cerin@univ-paris13.fr

Nicolas Greneche *LIPN UMR CNRS 7030 University Sorbonne Paris Nord* Villetaneuse, France nicolas.greneche@univ-paris13.fr

Tarek Menouer *Umanis Research & Innovation* Levallois-Perret, France tmenouer@umanis.com

*Abstract*—In cloud computing, elasticity is defined as "the degree to which a system is able to adapt to workload changes by provisioning and de-provisioning resources in an autonomic manner, such that at each point in time the available resources match the current demand as closely as possible". Adding elasticity to HPC (High Performance Computing) clusters management systems remains challenging even if we deploy such HPC systems in today's cloud environments. This difficulty is caused by the fact that HPC jobs scheduler needs to rely on a fixed set of resources. Every change of topology (adding or removing computing resources) leads to a global restart of the HPC jobs scheduler. This phenomenon is not a major drawback because it provides a very effective way of sharing a fixed set of resources but we think that it could be complemented by a more elastic approach. Moreover, the elasticity issue should not be reduced to the scaling of resources issues. Clouds also enable access to various technologies that enhance the services offer to users. In this paper, our approach is to use containers technology to instantiate a tailored HPC environment based on the user's reservation constraints. We claim that the introduction and use of containers in HPC job schedulers allow better management of resources, in a more economical way. From the use case of SLURM, we release a methodology for 'containerization' of HPC jobs schedulers which is pervasive i.e. spreading widely throughout any layers of job schedulers. We also provide initial experiments demonstrating that our containerized SLURM system is operational and promising.

*Index Terms*—HPC and cloud computing, Containers, Security, Operating system / middleware layers.

## I. INTRODUCTION

Both cloud computing and HPC (High Performance Computing) systems aim at sharing hardware resources between processes. Their respective architectures are very similar and share common principles. They have a mastermind that knows available resources and dispatch jobs on workers that run on compute nodes to compute the result of a job. In HPC, the mastermind is called a Scheduler whereas, in Cloud Computing, it is referred to as an Orchestrator. Even though their goal is similar, they have different properties [1]. These properties were related to the emergence and resurgence, more than ten years ago, of new concepts in Operating Systems (OS), in particular virtualization and containerization, which are closely related to system process management.

Schedulers technology aims at running jobs on compute nodes. A job is a set of tasks that may have a dependency relation, for example, to take into account preparing inputs, computing, and formatting outputs. When the compute node receives the task, it spawns system processes to execute it on the hardware. This is a very efficient functioning, simple and close to the hardware. The drawback is that Schedulers run on a fixed set of hardware resources and every change in the topology leads to a restart of the whole HPC infrastructure. This is also closely linked to the way an HPC center works, which relies on a huge set of homogeneous resources that people have bought once and almost for all thanks to massive funding. This makes the HPC cluster an efficient but very static way of handling resources and jobs. Originally, HPC architecture was designed to run only computational job making it impossible to reuse hardware for other purposes, for instance for high throughput I/Os with disks.

Orchestrators aim at running jobs in a Cloud infrastructure. The main difference between Cloud and HPC universes is the concept of elasticity. Cloud can interact with provisioning components and dynamically auto-scale available resources to fit the needs of tenants. Clouds are also able to run more generalist jobs, from the persistent Web site to a Hadoop cluster. Jobs can all share the same hardware infrastructure.

The organization of the paper is according to six sections including the introduction that serves to present the context. Section II introduces related works on containers integration in HPC environment and makes a positioning that defines the problem. Section III introduces a statistical survey we performed to motivate our approach. In Section IV we dive into the methodological aspects and implementation details of our solution. Section V is related to experimental work. Section VI concludes the paper and proposes future directions.

# II. RELATED WORKS

The goal of this section is twofold. First, we introduce some terminologies related to isolation technologies as well as the way they have been used to add some elasticity to HPC infrastructures. Then, we review research papers that are relevant for our targeted issues.

#### *A. Terminology*

Containerization does not target a whole OS but a set of one or more system processes. These system processes are called containers. When the host has to build a container, the kernel starts by grouping system processes independently from the parent/child model. A container can be composed of horizontally picked up system processes. The processes groups are called Cgroups with Linux and JobObjects on Windows systems. The groups are implemented through dedicated kernel system process data structures. The kernel has also several accounting drivers to monitor processes groups and resource consumption in order to limit and to control their usage. Moreover, the kernel also supplies a way to create multiple instantiations of objects such as user namespace, network stack, or users PID index to create an isolated namespace for process groups. All these technologies are combined to supply a sandboxed environment for system processes also called containers.

An Orchestrator deals with containers placement, on nodes of a Cloud infrastructure. Nodes can be either physical servers or virtual machines, depending on the provisioning workflow that comes with a container engine. When a container creation is requested, the Orchestrator elects a node based on available resources and asks the container engine to create it.

The Open Container Initiative1 (OCI), gathering major cloud providers is developing open industry standards around container formats and runtimes. The OCI currently contains two specifications, namely the Runtime Specification and the Image Specification. The Runtime Specification outlines how to run a "filesystem bundle" that is unpacked on disk. In the container world, the runtime is responsible for creating and running the container. We may think that the OCI is acting only at the low level of container runtime specification and that the end-user also needs to pull images, to build images, and to do some checksums. It is not the role of the OCI to manage such issues.

Kubernetes, which is a container orchestrator above the runtime layer, does not create containers itself. This task is delegated to container runtimes and Kubernetes must, therefore, be able to talk to several of them, each with a different API. The problem was eventually taken the other way, Kubernetes created an interface, namely Container Runtime Interface (CRI), which defines how Kubernetes talks to container runtimes. It is then up to them to implement or not the calls defined in CRI.

## *B. Relevant works and projects*

In HPC environment, isolation is used at different levels. In [2] an architecture for an on-demand HPC Clusters are built upon virtualization. The scheduler interacts with virtualized computing nodes providing a tailored HPC cluster. This approach provides better resources granularity than the work in [3] related to yet another Cluster On Demand (COD) architecture, made of a subset of physical nodes. Some platforms, like G5K [4], also use virtualization to enhance their offer to users. G5K was originally built for HPC experiments

1https://opencontainers.org/

on physical hosts but the community added Cloud oriented services that rely on Virtual machines (VMs) provisioning.

HPC schedulers also make use of containerization essentially to run self-contained custom images of applications in an efficient and secure way. When an application is containerized, it is shipped with all its dependencies. As a result, the image can run directly on the container engine with no need to add libraries on the host. This is more convenient, both for users to run their customized applications [5] and for administrators because they no longer have to combine multiple versions of the same application. Moreover, applications do not suffer drastically from performance degradation caused by virtualization, especially in the I/O [6] context. However, one drawback is that container engine like Docker can effectively be used to get root access on the host. Some wrappers have been developed to mitigate this risk [7].

Cloud providers operate large scale orchestrators to efficiently place jobs on their infrastructure. Google opened the source code of its own infrastructure, called Kubernetes and, formerly known as Borg [8]. Alibaba uses Fuxi [9] and released traces for analysis [10] by communities. Amazon and Microsoft respectively rely on Elastic Container Service (ECS) and Azure Container Instances (ACI). All these cloud providers have their dedicated HPC offers.

Users invoke a container engine that executes a program in the filesystem context supplied in the image. Some containers engines are privileged daemons running on the node to create containers. HPC oriented containers engines do not use privileged daemon. We now introduce, after a short presentation of Linux namespaces, three daemonless containers engines widely used in HPC (Shifter, Singularity, and Charliecloud) as well as two daemon based engines (Docker and CRI-O).

*1) Linux Namespaces:* Namespaces are kernel objects that can be multi-instanced on the host. There are six namespaces in the eco-systems of kernels. Five of them are called privileged namespaces because they require root privileges to unshare from the host. The privileged namespaces are :

- Mount for filesystem tree and mounting of the image;
- PID (Process IDs) are different inside and outside the container;
- UTS: Hostname and domain name;
- Network: container has its own network stack;
- IPC (Inter-Process Communication) isolation.

The unprivileged namespace is the user namespace. When a process forks a child and unshares the user namespace with it, a UID map is created. This map enables the child process to have a separate set of UIDs. When the new namespace is created by an unprivileged user, actions outside of the namespace are mapped to its EUID. HPC containerization heavily relies on user namespace because it enables unprivileged users to run untrusted programs.

*2) Containers engines:* Shifter [11] opened up the path to containerization in HPC environment. It relies only on SUID and chroot() making it very portable from one Unix based OS to another. Contrarily to other containers engines, Shifter does not use Cgroups or namespaces. As a consequence, UID inside and outside of a Shifter container are the same. However, Shifter operates well in the context of parent/child system processes hierarchy model.

Singularity [12] came after Shifter. User namespaces provide isolation of users. Singularity, if installed with Setuid bit on executable can also unshare other namespaces with the host kernel (IPC, PID, Network Stack). Moreover, Singularity includes several optimizations to reduce the impact of containerization on performance.

Charliecloud [13] is the newest protagonist in HPC containers technology. It's a lightweight alternative to Singularity. Charliecloud only offers user namespaces kernel isolation, drastically reducing the attack surface of source code.

Docker [14] is the first daemon based container engine. Its original design was a very monolithic one. The daemon handled image creation, publication, pull, push as well as running, topping, and monitoring the container. The daemon runs as root. As a consequence, the containerized application also runs as the "real" root (even if the container uses a dedicated user namespace). Such an amount of required privileges, combined with a vast surface of attack inherent in monolithic applications, made it unusable in HPC environments. However, it should be highlighted that efforts have been made to separate components of Docker to increase security by privilege separation as well as the integration of modularity principles with other applications.

CRI-O [15] is a lightweight alternative to Docker. CRI-O is designed with privilege separation in mind [16]. CRI-O is also developed to operate with Kubernetes as the default container engine.

*3) Overview of recent works:* Now, after this introduction of technological elements, we review the literature through a selected set of research papers using these technologies.

In [17] authors introduce three articles published with IEEE Internet Computing magazine, with a focus on micro-services and containers. All of them are related to our context. The first two focus on how micro-services should best be used, whereas the third provides a case study of containerization in a specific application context, namely network isolation. Amirante and Romano authored [18] "Container NATs and Session-Oriented Standards: Friends or Foe?" and they observe that Docker isolates applications by providing them one Internet Protocol (IP) address and then translating that using "network address translation" for use outside the container. In our paper, we are also faced with this problem and we solve it by relying on Kubernetes network security policies supplied by network plugins.

In [19] authors studied the potential use of Kubernetes on HPC infrastructure for use by the scientific community. They directly compared both its features and performance against Docker Swarm and bare-metal execution of HPC applications. They made some hypothesis regarding the accounting for operations such as (1) underlying device access, (2) inter-container communication across different hosts, and (3) configuration limitations. They discovered some limitations that showed that Kubernetes presents overheads for several HPC applications over TCP/IP protocol. Our work takes also into account this system-level but we consider the native container support of Linux rather than a dedicated (Kubernetes) overlay.

In [20] authors argued that HPC container runtimes (Charliecloud, Shifter, Singularity) have minimal or no performance impact. To prove this claim they ran industry-standard benchmarks (SysBench, STREAM, HPCG). They only found modest variation in memory usage. They invite the HPC community to containerize their applications without concern about performance degradation.

Another work demonstrating the utility of containers for HPC users is the work done by Sande Veiga et al. in [21]. The paper introduced the experience of PRACE (Partnership for Advanced Computer in Europe) in supporting Singularity containers on HPC clusters and provides notes about possible approaches for deploying MPI applications using different use cases. Performance comparison between bare metal and container executions are also provided, showing, as with [20], a negligible overhead in the container execution in a HPC context.

In [22] authors made a focus on production biological simulations over containers technologies. They studied the scalability and portability issues. They analyzed the productivity advantages of adopting containers for large HPC codes, and they quantified performance overhead caused by the use of three different container technologies (Docker, Singularity, and Shifter), comparing them to native execution. In this work, authors made experiments up to 256 computational nodes (12k cores) and they also considered three different HPC architectures (Intel Skylake, IBM Power9, and Arm-v8). They concluded that Singularity offered the best compromise.

In [23] authors main concern is to define a model for parallel MPI application DevOps and deployment using containers to enhance development effort and provide container portability from laptop to clouds or supercomputers. First, they extended the use of Singularity containers to a Cray XC-series supercomputer and, second, they conducted experiments with Docker on Amazon's Elastic Compute Cloud (EC2). Finally, they showed that Singularity containers operated at native performance when dynamically linking Cray's MPI libraries on a Cray supercomputer testbed. They also concluded that Amazon EC2 environment may be useful for initial DevOps and testing, while scaling HPC applications better suited for supercomputing resources like a Cray.

In [24] authors studied the portability and reproducibility issues of HPC containers. They focused on the current approaches used in many HPC container runtimes. They pointed out that the use of these approaches is still ad-hoc, test the limits of container workload portability, and several gaps likely remain. They suggested tackling the limitations through custom container label tagging and runtime hooks as a first step in managing HPC system library complexity. This may appear, at a first look, as an opposite argument for portability.

In [25] authors use Kubernetes and SLURM to build an infrastructure with two stages of scheduling. Their architecture is composed of one Kubernetes orchestrator and several SLURM HPC clusters. The user submits a custom kind of job called SlurmJob to Kubernetes orchestrator. That is when the first stage occurs. Kubernetes selects one of the SLURM driven HPC cluster according to resources requested by the user. When the job reaches the HPC cluster, SLURM schedules the job. This architecture is very similar to Grids [26] with a higher level of elasticity. The job itself is a singularity container.

#### *C. Positioning*

In this paper, we propose to containerize the HPC job scheduler itself, making it cohabit with all other sorts of jobs of the underlying cloud system. The rationale is to enable dynamic instantiation of HPC clusters infrastructures under the supervision of standardized orchestrators. In our experimentation, we use Kubernetes for orchestration with CRI-O as the container engine and Calico as the network plugin. We also use SLURM for HPC job scheduling.

All the cited works only use containers to run the users jobs on an HPC cluster. Roughly speaking, the HPC scheduler forks a container that runs the user's program. Our work is different because we containerize the HPC scheduler itself.

Summarizing, in this paper we sketch and we evaluate the possibility to run an HPC Scheduler upon an orchestrator, providing a tailored environment for users. This approach opens the path to two use cases:

- 1) A user, on-demand, can run a volatile fully containerized instance of a mono-user HPC cluster;
- 2) An "administrative" authority can instantiate a persistent multi-users HPC cluster.

#### III. MOTIVATING EXAMPLE

To get an intuition about the benefit of our approach in terms of resources utilization, we conducted a statistical survey on several HPC centers working with SLURM as the HPC job scheduler. We collected statistics related to the number of jobs and their CPU efficiency on a 6 months period. We received responses from many HPC centers of different size. We divided the results into four categories:

- 1) Laboratory scale;
- 2) University scale;
- 3) National scale;
- 4) Specialized HPC infrastructure;

The first three categories are related to the nature of the HPC Cluster. However, all of them are multi-purposed infrastructures. They mix CPUs and GPUs. Our survey only concerns CPUs. The fourth category is a specialized HPC cluster dedicated to a specific use. For each category we considered the number of jobs, the average efficiency as well as the median.

Table I is a synthesis of the results of the survey. We considered four values. The first is the number of jobs executed within the 6 months study.

Then, we have the average efficiency of jobs. The formula is given by:

$CPUefficiency=TotalCPU/Alloc CPUs/Elapsed$ (1)

| Category | Jobs | Average | Median | Overall |
| --- | --- | --- | --- | --- |
| 1 | 548 | 43.47 | 4.16 | 73.4 |
| 2 | 2366 | 75.17 | 99.73 | 63.36 |
| 3 | 967652 | 38.43 | 47.67 | 46.64 |
| 4 | 2080 | 85.51 | 99.43 | 88.85 |

TABLE I: CPU efficiency statistical analysis results

In (1), TotalCPU is the sum of System CPU (amount of system CPU time used by the job) and User CPU (amount of user CPU time used by the job), AllocCPUs is the number of CPU allocated to the job and Elapsed (job elapsed time).

The median of jobs CPU efficiency is derived from previously computed efficiency. Another view for the median analysis can be found in Figure 1 where a boxplot for each category has been drawn.

The Overall efficiency is the time spent in computing for whole jobs reported to the sum of elapsed time of jobs:

$$\sum_{TotalCPU}/\sum_{Alloc CPUs}/\sum_{Elapsed}\tag{2}$$

Then, we tried to represent the bad impact of each job on the whole HPC cluster. The formula for each job is:

$$B a d I m p a c t=W a s t e d J o b C P U T i m e/O v e r a l l E l a p s e d$$

(3) In (3), *WastedJobCPUTime* is the opposite of CPU efficiency. It represents the CPU time not used by the job (making IO). The *OverallElapsed* is the sum of elapsed time of each job. Figure 2 is a scatter point graph for each category. Each point is a job with efficiency (percentage of CPU time used) on the Y axis and its bad impact factor on the X axis.

The conclusion of this study is that multi-purposed HPC systems (categories 1, 2, and 3) do not maximize CPU efficiency. There are several potential reasons for such waste. First, the job may be more IO intensive than CPU intensive. Second, we can notice from Table I that the CPU efficiency of category 3 is the worst among the results. This can be explained by the fact they also supply very large storage for jobs that require a lot of IO. Summarizing, we think that there is a potential for improvement for the efficiency of a HPC system. We will study the feasibility of cohabitation of HPC jobs with far less greedy generalist jobs (like running a small website) on a fully containerized environment. Indeed we promote the multiplexing of online jobs with batch workloads, in considering that an HPC infrastructure is a batch workload, executing batch jobs.

#### IV. METHODOLOGY FOR SLURM CONTAINERIZATION

In order to make our work concrete, we decided to go with the well established Kubernetes technology which we may consider as a de-facto standard. Kubernetes orchestrates pods on hosts. A Kubernetes pod is a group of containers that are deployed together on the same host. In our proposed architecture, illustrated in Figure 3, a pod is composed of a Slurmd or Slurmctld container and a Munge process. As shown in Figure 4, a user submits a job to Slurmctld then Slurmctld dispatch it to Slurmd instances on compute nodes.

![](_page_4_Figure_0.png)

![](_page_4_Figure_1.png)

![](_page_4_Figure_2.png)

![](_page_4_Figure_3.png)

This implies communication between Slurmctld and Slurmd processes. Each message is authenticated through a local Munge daemon running on each node. In Figure 3, each containerized Slurmd or Slurmctld is backed with Munge within a Pod. It should be highlighted that any other HPC job scheduler can be containerized this way.

## *A. Containerization of Slurmctld*

As we have just noticed, Slurmctld and Munged are key components. Listing 1 is the proposed snippet of code of the Kubernetes manifest for Slurmctld. Slurmctld can be containerized like any other common program. It does not require capabilities or any other privileges. This program only binds on an unprivileged network port and eventually connect

Fig. 3: Containerized SLURM integration in Kubernetes.

Namespace D 

![](_page_4_Figure_8.png)

to a database if slurmdbd is used. The Security Context is set to run the pod as an unprivileged user (UID = 1000, lines 6 and 7).

The pod is made of two containers, one for Slurmctld (line 12 to 16) and another for Munged (lines 17 to 21). Munged is required to cipher communications between Slurmd workers and the slurmctld master. Slurmctld container talks to Munged container through a local UNIX socket located on an emptyDir (lines 9 and 10) which is a shared volume between the two containers.

It should be highlighted that the Munged container is optional. If the pods are running on a dedicated Kubernetes namespace (not to be confused with user namespaces mentioned in a previous section) with a network isolation through Network Policies, Munged can be disabled. If munge is enabled, all the daemons of our architecture must share the same private key (eventually shared on a ReadOnlyMany capable Physical Volume).

#### *B. Containerization of Slurmd*

Listing 2 is our proposition for the snippet of code of the Kubernetes manifest for Slurmd. Slurmd is more tricky to containerize because of the requirements of resources limitation and security. By default, a container has no restrictions on resource consumption on the host. These limitations are enforced by Cgroups. The container engine instantiates slurmd within a Cgroups and configures subsystems to match the resources required by the user. In slurmd manifest shown in Listing 2, 8 CPUs are required (line 15 and 16) and the container won't be able to use more than 8 CPUs (line 13 and 14). This is equivalent to a Slurmd node configured with 8 CPUs. Only the root user can create a Cgroup. The use of an unprivileged container engine i.e. launched by a non-root user is therefore impossible. As a consequence, the use of a privileged containers engine implies security issues.

## Listing 1: Slurmctld manifest

![](_page_5_Figure_4.png)

#### Listing 2: Slurmd manifest

![](_page_5_Figure_6.png)

25 nodeSelector: 26 type: compute

*1) Resources limitation:* Slurmd requires to know how many CPUs are usable on the host it belongs to. Figure 5 shows the different Linux features used by bare-bone or virtualized slurmd to get the number of CPUs available on the host. CPU probing is implemented in file *xcpuinfo.c* of Slurmd source code. Slurmd can natively relies on two mechanisms: *hwloc* [27] (if available) or *sysconf()*. Hwloc enables us to get an accurate map of CPU resources. The *sysconf()* (more specifically get *nprocs()*) function, reads the */sys* filesystem to get the number of available CPUs . This information is less accurate because there is nothing about the topology of CPUs.

![](_page_5_Figure_9.png)

Fig. 5: Slurmd CPU probing.

Regarding Cgroups, an additional layer of CPU probing must be added to Slurmd to enable detection of limits imposed by the Cgroup. This additional layer reads the information stored in */sys/fs/cgroup/cpu,cpuacct* and more specifically files *cpu.cfs quota* us (the total available run-time within a period) and *cpu.cfs period* us (the length of a period). The division of *cpu.cfs quota* us by *cpu.cfs period* us gives the number of available CPUs for the container and required for Slurmd dynamic configuration.

*2) Security of container engine:* As stated in [5], [7], [11], [12], [20] and [23] usage of privileged daemonized container engines is strongly not recommended in the HPC environment. However, in multipurpose Cloud environments, orchestrators rely on this kind of container engine. In the related work mentioned above, the Docker implementation is explicitly criticized.

The main security concern with Docker is due to its monolithic origins that provide a vast surface of attacks to hackers, resulting in multiple CVE (Common Vulnerabilities and Exposures). However, various security countermeasures are implemented in Docker [28] to harden the container engine against the execution of untrusted images. Moreover, there are security-oriented wrappers to launch Docker images from HPC schedulers. Socker [29] is a Docker secure wrapper callable by Slurm.

In our work, we use CRI-O which is another daemonized container engine. Its main asset, regarding security, is that it has been developed with modularity in mind. This provides a timely privilege separation.

*3) Security of container runtimes:* A container engine calls a container runtime to run the container. People can combine almost any kind of runtime with any engine thanks to Open Containers Initiative (OCI). The default *runc* can be changed by another one that provides stronger isolation. Kata Containers [30] hardens isolation by adding a layer of virtualization to the container, whereas gVisor [31] provides a user-space kernel. Both of them enforce stronger isolation for Slurmd container.

![](_page_6_Figure_1.png)

## *C. Discussion about the methodology*

We would now like to explain how what is proposed is general and not anchored in one and only one artifact, in this case, Kubernetes. It should simply be noted that Figure 3 can be generalized by replacing Slurmd and Munged with the corresponding daemons of other HPC job schedulers. Then we also need a network backend and a runtime. We have chosen CRI-O and Calico in our explanations. We could use runc, promoted by OCI, as another runtime but, as we have explained, we have security issues and this is not our option. The experimental part is precisely carried out by considering several runtimes.

## V. EXPERIMENTATION

For our experimental work, we dedicated three physical nodes to install the small Kubernetes cluster described in Figure 6. This experimentation aims to check if the HPC job scheduler containerization behaves in a correct way for bagof-tasks as well as with HPC related technologies such as Message Passing Interface (MPI) which are more challenging. The first series of experiments can be considered as unitary tests. The second series is a preliminary test for performance evaluation.

As depicted in Figure 6 we have a node with three VMs. The first VM is an NFS server to provide Physical Volume (PV) with ReadWriteMany property for our containers. The second VM is the API-Server of our Kubernetes Cluster. This is the master node of our infrastructure. The third VM is a node of the Kubernetes architecture. This node is labeled as "backend". In lines 22 and 23 of Listing 1, the slurmctld pod will be scheduled on this backend node. Finally, we have two physical nodes labeled as "compute". These nodes will host the slurmd containers, as we can see in lines 25 and 26 of Listing 2.

## *A. Unitary tests*

All our experimentations used the CRI-O container engine. In this scenario we tested the following runtime: runc, Kata

| C | MPI | OMP threads |  | MPI ALL REDUCE |  | TFLOPs |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | min | max | avg |  |
| 0 | 4 | 28 | 3.04 | 7.83 | 5.11 | 1.62 |
| 2 | 2 | 56 | 2.91 | 9.22 | 4.91 | 1.48 |
| 4 | 4 | 28 | 2.86 | 9.31 | 5.06 | 1.47 |
| 8 | 8 | 14 | 2.92 | 10.02 | 5.12 | 1.46 |
| 16 | 16 | 7 | 2.87 | 9.76 | 5.03 | 1.47 |

TABLE II: Benchmark

Container with Qemu and Firecracker sandboxing, and gVisor. The containers execute an MPI program and the executions, for each context, were correct.

## *B. Towards a performance evaluation of our system*

We made an early benchmark to evaluate, first the impact of full containerization of Slurm on CPU efficiency and second, the impact of Calico network overlay on MPI communication. We used HPCG version 3.1. We made a first-round without any containerization. Our experimental platform is made of two computing nodes. Each node has two CPUs Intel Xeon Gold 5120 with 14 hyperthreaded cores and 96G of RAM. In the first round, we did not use any containerization and run the benchmark directly on hardware with Slurm on the two nodes. We ran HPCG in hybrid mode with 2 MPI process per node (to match the number of sockets) and OMP NUM THREADS set to 28 to match the number of hyperthreaded cores. We know that performance would have been better if we set OMP NUM THREADS at 14 (to match only physical cores). But we do not want to get the highest performance rate. We just need to have reference values to quantify the impact of our solution.

After this first round, we ran one containerized Slurm per node with 1 MPI process per container and OMP NUM THREADS set to 56. Slurmd is configured with the CPUs=56 in its configuration file. Then, we ran two containerized Slurm per node with 1 MPI process per container and OMP NUM THREADS set to 28. Slurmd is configured with the CPUs=28 and so on. Results are reported in Table II where C is the number of Slurmd containers, MPI the number of MPI processes, OMP threads the value of OMP NUM THREADS, DDOT MPI ALL REDUCE values (min, max, and average) and the TFLOPs.

We observe on Table II that networks overlay do not have a significant impact on MPI operations. The only noticeable loss of performance is when we containerize Slurmd. This is likely to be related to the fact that the pair MPI process number and OMP threads do not match the physical layout of sockets and cores. There is no noticeable performance degradation with containerized Slurmd. So, our approach seems to fit an HPC context.

#### *C. Complementary work*

We also developed a patch for Slurmd making it conscious of Cgroups resources limitation. That was mandatory in former versions of Slurmd because the daemon refused to start if the resources seen on the host did not match those defined in the configuration file. It should be noticed that Slurm comes now with the *–enable-multiple-slurmd* compilation directive that enables multiple Slurmd running on the same host. One of the consequences is that even if the verification fails, Slurmd starts. This work has been developed for backward compatibility with older versions of Slurmd.

#### VI. CONCLUSION

In this paper, we put forward a methodology for the containerization of HPC job schedulers. The main difference between our work and many works related to container technology in an HPC environment, among them [25], is that we containerize the scheduler itself. As a consequence, the orchestrator and the HPC scheduler are not aware of their respective existence. This approach is less static than HPC oriented ones and makes it possible to run any kind of containers technology inside our containerized HPC job scheduler since we have demonstrated certain modularity for our proposal.

As future work, we propose to fully benchmark our approach and methodology through HPC intensive applications. The objective is to evaluate the overhead of the technique if any. We would like to emphasize that our approach is complementary to classical HPC architecture. Another future work is to evaluate the possibility to extend classical non containerized HPC job scheduler with containerized ones to build a hybrid and elastic architecture. The idea would be to have a static part in the HPC architecture, coupled with an elastic one.

We acknowlege USPN IT service for their support as well as MAGI HPC cluster team.

## REFERENCES

- [1] G. Mateescu, W. Gentzsch, and C. J. Ribbens, "Hybrid computing - where hpc meets grid and cloud computing," *Future Generation Computer Systems*, vol. 27, no. 5, pp. 440 – 453, 2011.
- [2] Yang-Suk Kee, C. Kesselman, D. Nurmi, and R. Wolski, "Enabling personal clusters on demand for batch resources using commodity software," in *2008 IEEE International Symposium on Parallel and Distributed Processing*, pp. 1–7, 2008.
- [3] J. S. Chase, D. E. Irwin, L. E. Grit, J. D. Moore, and S. E. Sprenkle, "Dynamic virtual clusters in a grid site manager," in *High Performance Distributed Computing, 2003. Proceedings. 12th IEEE International Symposium on*, pp. 90–100, 2003.
- [4] D. Balouek, A. Carpen-Amarie, G. Charrier, F. Desprez, E. Jeannot, E. Jeanvoine, A. Lebre, D. Margery, N. Niclausse, L. Nussbaum, O. Richard, C. Perez, F. Quesnel, C. Rohr, and L. Sarzyniec, "Adding ´ Virtualization Capabilities to the Grid'5000 Testbed," in *Cloud Computing and Services Science* (Ivanov, IvanI., Sinderen, Marten, Leymann, Frank, Shan, and Tony, eds.), vol. 367 of *Communications in Computer and Information Science*, pp. 3–20, Springer International Publishing, 2013.
- [5] L. Benedicic, F. A. Cruz, A. Madonna, and K. Mariotti, "Sarus: Highly scalable docker containers for hpc systems," in *High Performance Computing* (M. Weiland, G. Juckeland, S. Alam, and H. Jagode, eds.), (Cham), pp. 46–60, Springer International Publishing, 2019.
- [6] W. Felter, A. Ferreira, R. Rajamony, and J. Rubio, "An updated performance comparison of virtual machines and linux containers," in *2015 IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS)*, pp. 171–172, 2015.
- [7] A. Azab, "Enabling docker containers for high-performance and manytask computing," in *2017 IEEE International Conference on Cloud Engineering (IC2E)*, pp. 279–285, 2017.
- [8] B. Burns, B. Grant, D. Oppenheimer, E. Brewer, and J. Wilkes, "Borg, omega, and kubernetes," *Queue*, vol. 14, p. 70–93, Jan. 2016.

- [9] Z. Zhang, C. Li, Y. Tao, R. Yang, H. Tang, and J. Xu, "Fuxi: A faulttolerant resource management and job scheduling system at internet scale," *Proc. VLDB Endow.*, vol. 7, p. 1393–1404, Aug. 2014.
- [10] Y. Cheng, A. Anwar, and X. Duan, "Analyzing alibaba's co-located datacenter workloads," in *2018 IEEE International Conference on Big Data (Big Data)*, pp. 292–297, 2018.
- [11] D. M. Jacobsen and R. S. Canon, "Contain this, unleashing docker for hpc," *Proceedings of the Cray User Group*, pp. 33–49, 2015.
- [12] G. M. Kurtzer, V. Sochat, and M. W. Bauer, "Singularity: Scientific containers for mobility of compute," *PloS one*, vol. 12, no. 5, 2017.
- [13] R. Priedhorsky and T. Randles, "Charliecloud: Unprivileged containers for user-defined software stacks in hpc," in *Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*, SC '17, (New York, NY, USA), Association for Computing Machinery, 2017.
- [14] D. Merkel, "Docker: Lightweight linux containers for consistent development and deployment," *Linux J.*, vol. 2014, Mar. 2014.
- [15] *CRI-O : Lightweight Container Runtime for Kubernetes*, 2020 (accessed June 16, 2020). https://cri-o.io.
- [16] A. N. Habermann, L. Flon, and L. Cooprider, "Modularization and hierarchy in a family of operating systems," *Commun. ACM*, vol. 19, p. 266–272, May 1976.
- [17] F. Douglis and J. Nieh, "Microservices and containers," *IEEE Internet Computing*, vol. 23, pp. 5–6, nov 2019.
- [18] A. Amirante and S. P. Romano, "Container nats and session-oriented standards : Friends or foe ?," *IEEE Internet Computing*, vol. 23, no. 6, pp. 28–37, 2019.
- [19] A. M. Beltre, P. Saha, M. Govindaraju, A. Younge, and R. E. Grant, "Enabling hpc workloads on cloud infrastructure using kubernetes container orchestration mechanisms," in *2019 IEEE/ACM International Workshop on Containers and New Orchestration Paradigms for Isolated Environments in HPC (CANOPIE-HPC)*, (Los Alamitos, CA, USA), pp. 11–20, IEEE Computer Society, nov 2019.
- [20] A. Torrez, T. Randles, and R. Priedhorsky, "Hpc container runtimes have minimal or no performance impact," in *2019 IEEE/ACM International Workshop on Containers and New Orchestration Paradigms for Isolated Environments in HPC (CANOPIE-HPC)*, (Los Alamitos, CA, USA), pp. 37–42, IEEE Computer Society, nov 2019.
- [21] V. S. Veiga, M. Simon, A. Azab, C. Fernandez, G. Muscianisi, G. Fiameni, and S. Marocchi, "Evaluation and benchmarking of singularity mpi containers on eu research e-infrastructure," in *2019 IEEE/ACM International Workshop on Containers and New Orchestration Paradigms for Isolated Environments in HPC (CANOPIE-HPC)*, (Los Alamitos, CA, USA), pp. 1–10, IEEE Computer Society, nov 2019.
- [22] O. Rudyy, M. Garcia-Gasulla, F. Mantovani, A. Santiago, R. Sirvent, and M. Vazquez, "Containers in hpc: A scalability and portability study in production biological simulations," in *2019 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*, (Los Alamitos, CA, USA), pp. 567–577, IEEE Computer Society, may 2019.
- [23] A. J. Younge, K. Pedretti, R. E. Grant, and R. Brightwell, "A tale of two systems: Using containers to deploy hpc applications on supercomputers and clouds," in *2017 IEEE International Conference on Cloud Computing Technology and Science (CloudCom)*, (Los Alamitos, CA, USA), pp. 74–81, IEEE Computer Society, dec 2017.
- [24] R. S. Canon and A. Younge, "A case for portability and reproducibility of hpc containers," in *2019 IEEE/ACM International Workshop on Containers and New Orchestration Paradigms for Isolated Environments in HPC (CANOPIE-HPC)*, (Los Alamitos, CA, USA), pp. 49–54, IEEE Computer Society, nov 2019.
- [25] M. Bauer, "Solving Problems in HPC with Singularity. CernVM Workshop 2019," Jun 2019.
- [26] L. Smarr and C. E. Catlett, "Metacomputing," *Commun. ACM*, vol. 35, p. 44–52, June 1992.
- [27] F. Broquedis, J. Clet-Ortega, S. Moreaud, N. Furmento, B. Goglin, G. Mercier, S. Thibault, and R. Namyst, "hwloc: a Generic Framework for Managing Hardware Affinities in HPC Applications," in *PDP 2010 - The 18th Euromicro International Conference on Parallel, Distributed and Network-Based Computing* (IEEE, ed.), (Pisa, Italy), Feb. 2010.
- [28] T. Bui, "Analysis of docker security," *CoRR*, vol. abs/1501.02967, 2015.
- [29] *Socker : A wrapper for secure running of Docker containers on Slurm*, 2018 (accessed June 16, 2020). https://github.com/unioslo/socker.
- [30] *Kata Containers open source container runtime*, 2020 (accessed June 16, 2020). https://katacontainers.io.
- [31] *gVisor*, 2020 (accessed June 16, 2020). https://gvisor.dev.

