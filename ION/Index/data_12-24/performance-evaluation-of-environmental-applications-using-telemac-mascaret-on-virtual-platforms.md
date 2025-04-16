# Performance Evaluation of Environmental Applications using TELEMAC-MASCARET on Virtual Platforms

Minh Thanh Chung1, Manh-Thin Nguyen1, Nhu-Y Nguyen-Huynh1, Nguyen Thong2, Nam Thoai1

HPC Lab - Faculty of Computer Science and Engineering 1 Faculty of Civil Engineering 2 Ho Chi Minh City University of Technology, VNU-HCM

Ho Chi Minh City, Vietnam

Email: {minhchung}@cse.hcmut.edu.vn 1 , {nmthin,nhny,namthoai}@hcmut.edu.vn 1 , {nguyenthong}@hcmut.edu.vn 2

*Abstract*—Environmental issues can be simulated in High Performance Computing (HPC) systems such as simulating flood inundation. This paper presents the simulation of two problems in Vietnam using TELEMAC-MASCARET, namely flood and salinization of Ho Chi Minh city and Mekong Delta. Evaluating these simulations on both physical machines and virtualization platforms are introduced in detail. To meet the requirements of serving multiple users or different simulation problems, virtualization environment offers feasible solutions and ensures the availability as well as the flexibility. Besides the popularity of virtual machine (VM) in Cloud, recently there is a lightweight virtualization platform called Docker. In this paper, we propose a model for deploying TELEMAC on Docker. Then, we show evaluations through different scenarios when deploying TELEMAC on Docker and VM. Docker has more potential with the lightweight architecture, especially its overhead is nearly negligible. The performance of Docker is better than VM, and the execution time of TELEMAC can be reduced significantly. The execution time of VM is about 1.6 times longer than Docker in terms of running the simulations of environmentrelated problems in Vietnam.

*Keywords*-Environmental computing, TELEMAC, Docker, performance

# I. INTRODUCTION

Following the rising of environment-related problems, the methods of numerical simulations are playing an important role. The results of these simulations can make supports to estimate and prevent the damage caused by disasters. Besides the annual problem is flood inundation, Vietnam is suffering its worst drought in nearly a century with salinisation in the crucial southern Mekong delta. To tackle with these problems, the use of TELEMAC [1] is becoming popularly. However, the solutions using TELEMAC simulations need the power of parallel computing [2]. The TELEMAC system is one of suitable environmental simulation softwares that has developed rapidly. TELEMAC packages a whole processing chain for the calculation of water solute and sediment motions in the fluvial, coastal, estuarine, lacustrine and groundwater domains [3]. One of the most popular modules of TELEMAC using for environment-related issues in Vietnam is TELEMAC2D. This module provides the hydrodynamics that consist of horizontal depth-averaged velocities and water depth.

In terms of simulating the large scale environmental issues, the execution time and accuracy are two major criteria. Taking advantages of the developing in HPC system, parallelization is the best way to improve the efficiency of simulations. However, to meet the demand of multiple purposes, the simulation of each problem can be performed many times along with different simulation modules. Simultaneously, the implementation of these modules on different platforms or different operating systems (OS) is possible. To extend the idea providing computing infrastructure on Cloud, we survey the performance as well as the efficiency of two different virtualization platforms, namely, hypervisor and containerization.

The hypervisor-based virtualization known as virtual machines (VMs) has been used for a long time with many service providers, e.g., Amazon EC2, VMWare. Differ from the hypervisor technique, containerization is a lightweight virtualization platform that creates virtual instances called containers [4]. Docker [5] is a containerization platform which is being widely used and developed. From our previous research [6], Docker has more advantages than VM in terms of the computational capacity, the network performance and the ability of data access associated with data intensive applications. The difference between Docker and VM is the architecture. Docker has the architecture sharing resources with the host kernel, and this is one of reasons that makes Docker containers reduce the overhead. Docker also obtains compatibility with some advanced technologies such as InfiniBand (IB) network [7], Xeon-Phi co-processor [8]. From those features of Docker, we evaluate the real efficiency of Docker when deploying the TELEMAC simulation modules in practice. With the real problems and applications, the performance of Docker is still questionable. Besides, we propose a model of deploying TELEMAC on Docker for scalability and give some experiences when running TELEMAC in parallel. The improvement of efficiency and accuracy of TELEMAC needs to consider the configuration of parallelization. The survey of speed-up shows that the maximum amount of cores is not the best way for obtaining the shortest execution time.

The rest of the paper is organized as follows. Section 2 highlights the fundamental background about TELEMAC system and virtual platforms. In section 3 and 4, we present the motivation and previous related to our research. The experiences and model of deploying TELEMAC on Docker are shown in section 5. The next section reveals our performance results as well as evaluations about Docker and VM. Finally, we draw some conclusions and illustrate future work in section 7.

## II. BACKGROUND

# *A. TELEMAC modeling and Enviromental issues in Vietnam*

TELEMAC model or TELEMAC-MASCARET system was developed by the Electricity of France (EDF) Company, with the participation of many research organizations around the world. The TELEMAC-2D module is used to simulate free surface flows in two dimensions of horizontal-space (average in vertical direction). TELEMAC uses the Saint−Venant equations to simulate the free surface flow. These equations are derived from Navier-Stokes equations based on assumptions on the flow pattern and approximations by the free surface modeling. The Saint-Venant equations are shown as below:

$$\frac{\partial h}{\partial t}+\vec{u}.\Delta(h)+h\,d i v(\vec{u})=S_{h},\qquad\qquad(1)$$

$$\frac{\partial u}{\partial t}+\vec{u}.\Delta(u)=-\vec{g}\frac{\partial z}{\partial x}+S_{x}+\frac{1}{h}div(hv_{t}\Delta(u)),\tag{2}$$

$$\frac{\partial v}{\partial t}+\vec{u}.\Delta(v)=-\vec{g}\frac{\partial z}{\partial y}+S_{y}+\frac{1}{h}div(hv_{t}\Delta(v)),\tag{3}$$

where h is the depth of water; u and v are the velocity components; x and y are the horizontal coordinates; z is the free surface elevation, i.e., the elevation along with the vertical direction; g is the gravity acceleration; vt is the momentum diffusion coefficient; Sh, Sx and Sy are the sources or sink terms. There is a variety of simulation modules using standard algorithms to simulate or model environmental issues. Before running simulation modules, we need to set up a fine mesh to describe a simulated space. The fine mesh contains the numbers of elements and nodes in the form of unstructured grid.

For environmental issues, we concern two problems that are occurring in Ho Chi Minh city and Mekong Delta, namely flood inundation and salinization. Flood is one of natural disasters having the most impact in Vietnam. There are some kinds of floods. Some floods are induced by nature, but some floods are induced by the artificial structure, for example the dam-break. They can make a long term effect that people have to face a variety of damages within minutes or hours. Besides the flood inundation, that is the salinization in Mekong Delta. The prolonged salinization has damaged sugarcane plantation areas in several provinces of southern Vietnam. Over 2,300 hectares of sugarcane plantation has sustained damage, accounting for over 30 percent of the total crop.

The utilization of numerical simulations can provide helps for experts to estimate and prevent these phenomena through the predictions. Based on the theories of physics, the flood flow or salinization of the sea water can be treaded as a kind of fluid flows with free surface. We can simulate the water deep or the move of flood by the variant of the height of the free surface. TELEMAC is an open source software that is package and based on finite element method (FEM) to implement these large scale simulations as mentioned above. To deal with the large scale of the flow simulations, we need to the power of parallel computing represented by HPC system. In further, HPC leverages the large scale parallel computing for multiple tasks running different simulation modules.

## *B. Virtual platforms in HPC*

For HPC applications on large scale clusters, the scalability as well as management are becoming increasingly important. For example, the prediction of environmental issues needs the large scale parallel computing in simulation [9]. Besides, the power of HPC system is also employed in other simulation domains, e.g., Land Transformation Model [10], Social Simulations [11]. That is the motivation for leveraging the idea of using computer to emulate itself, namely virtualization. There are many virtualization technologies recently. One of them is virtual machine based on hypervisor-based virtualization. Moreover, we have a new platform based on the lightweight virtualization technology called Docker [5]. The key differences between these two platforms are the architecture and the operation mechanism.

1) *Virtual machine*: VMs have been popular with the architecture relied on hypervisor-based architecture. The original idea of VM is the virtualizing of an entire system. It means that each VM is virtualized from hardware to OS software. Therefore, hypervisor layer plays a vital role in managing VMs [12]. It allocates and controls the resources of physical machine (PM) for guest domains. Furthermore, this layer not only emulates devices to guest domains, but also simplifies the physical architecture to virtualize. There are two types of hypervisor [13], including:

- Type-1, native or bare-metal hypervisors: These hypervisors run directly on the hardware of host to manage resources for guests. Some hypervisors are known as the Citrix XenServer, Microsoft Hyper-V, and VMware ESX/ESXi.
- Type-2, or hosted hypervisors: Differ from the previous type, these hypervisors run on the operating system from host. VMs deployed by these hypervisors are considered as a running process on the host machine, for examples, VMware Workstation, VMware Player, Virtual Box.

Besides, there are some hypervisors build on the hybrid architecture of type-1 and type-2, e.g, Kernel-based Virtual Machine (KVM) [14], FreeBSDs bhyve. VMs can greatly benefit cluster computing in such systems [15], especially from the following aspects:

![](_page_2_Figure_0.png)

**Virtual Machines Containers**

**Bins/Libs App 1**

Fig. 1. The architecture of VM and Docker.

- Availability and Scalability: Virtual infrastructure can provide a large amount of resources from physical system and make them accessible. Concurrently, a service provider can expand the volume of virtual resources or shrink them.
- Complete isolation and security: Each VM is considered as a whole system consisting of hardware and software. Thus, their operation space can be ensure the isolation among VMs and PM. The state of guest can be recovered and controlled by Virtual Machine Monitor (VMM) when malicious codes crash the virtual system. • Ease of management: An administrator may create or
- delete, start or shutdown a VM easier than a real machine. We can observe VMs along with additional information running inside each instance.
- Customization: The customization feature shows that we can modify both the specification of hardware and software before generating a guest, for example, CPU, RAM.

Overall, the deployment of HPC application on VM environment is similar to PM. A parallel application need three requirements in a distributed system: parallelization of that application, communication of compute nodes and parallel libraries such as Message Passing Interface (MPI).

2) *Docker*: In contrast, Docker platform leverages a lightweight architecture named containerization. In principle, Docker emulates their instances called containers at the abstraction level of OS. It is noticeable that Docker shares the same kernel with the host machine. Two containers do not need to concern the limitation of resources before creating them, they can scale up or down the use of all resources on PM. If containers are not running anything, they do not generate extra overhead. They only perform applications in spaces that are isolated from other containers and the host OS [16]. The operation model of Docker is client-server. At the client side, Docker has a set of commands to request the server. Inside Docker, there are three main components [5] Docker images, Docker registries and Docker containers. Concretely, Docker image is a read-only template that plays a role in creating Docker containers. Then, Docker registry is a place which stores Docker images. There are the public registry and the private registry known as the local registry in the host. The public Docker registry has a huge collection of images for using, it is provided with Docker Hub. The rest of Docker is Docker container that is equivalent to a directory holding everything. A container can wrap things needed for running application. Docker architecture facilitates to run, start, stop, move, migrate virtual instances faster than VM.

This paper does not go into detail about the implementation of Docker. Docker makes use of several kernel features to deploy containers. Firstly, related to the virtualization at the OS level, Docker implements the isolation by using namespaces technology. Each container has a set of namespaces to define its own workspace such as PID, NET, IPC, MNT, UTS. One more feature is sharing resources with the host kernel. Docker needs a Limux kernel component called ControlGroups or cgroups to allocate and manage resources for each container. This can reduce the overhead when scale up the amount of generated containers using resources. As Figure 1 shown, if two Docker containers use the same libraries to run their applications, they can share these libraries of related dependencies. When comparing the architecture of Docker to VM, the hypervisor layer of VM provides an entire environment to each instance. The hypervisor creates virtual devices, privileged instructions, virtual memory address to isolate the operation space of VM with the host and others. Therefore, every malicious code crashing VM can recover because the resource integrity of PM is controlled by hypervisor. This is one of strong points about the security feature of VM in comparison with Docker. However, for the lightweight features, Docker is better than VM through reducing the overhead significantly and optimizing the use of resources.

# III. MOTIVATION

Environmental issues are harmful effects of human activity that need an integration of solutions in all of related fields. Especially, HPC plays an important role in simulating and predicting the phenomena of environment. Associated with the simulation, the use of TELEMAC in recent years is being popular in Vietnam. For example, Vietnam's Mekong Delta is facing the most severe drought and salinization. Salinization is a worldwide problem affecting to not only land and water, but also the human life [17]. More importantly, the solution of using sequential execution is not efficiency with the large scale problems. That is the reason why the parallel computing is becoming extremely important.

However, along with the expand of demand of using parallel computing resources, physical system cannot support multiple users requiring different operating systems as well as different purposes in simulation. Virtual platforms are feasible solutions. Besides VMs that have been used for a long time, there is a new platform supporting benefits in Cloud environment with the low overhead, namely Docker. In previous research [18], we survey the performance between Docker and VM. Our evaluation reveals that Docker has more potential than VM in some aspects, e.g., the computational capacity, the ability of data access, high throughput with the compatibility on InfiniBand infrastructure. That is a question whether Docker obtains the efficiency when running HPC applications such as TELEMAC in parallel. We propose a model of deploying TELEMAC tool on Docker environment to meet the demand of scalability.

Our evaluation shows early experiences of using Docker container to support computing infrastructure into environment-related simulations. For example, the use of TELEMAC is to simulate the status of salinization in Vietnam.

# IV. RELATED WORKS

The integration of parallelization and simulation can achieve the high efficiency in various domains like civil engineering and transportation engineering. TELEMAC is a powerful open source used to simulate free-surface flows in two dimensions or three dimensions. HPC system is contributing the computing ability to the development of TELEMAC [19]. There is a variety of researches using TELEMAC to tackle the practical problems related to environment such as [20], [21]. The simulation results of TELEMAC facilitate to prevent the natural disasters. To improve the performance of integrating TELEMAC and parallel computing, several projects are initiated. For example, the hybrid programming model using MPI and OpenMP in TELEMAC to improve the parallel performance [9]. We approach the expand of idea providing the computing platforms on Cloud. Two virtualization technologies considered in this paper are VM and Docker container. From the evaluation [6] on our system with the integration of InfiniBand network, the performance of Docker and VM is evaluated through different aspects. Recently, there are some researches that compare the backgrounds of Docker architecture to VM [22] or evaluate criteria related to the operation of Docker and VM such as I/O access, TCP network, computing ability [23]. The previous results of our evaluations show that Docker has more potential in HPC field, especially when running different benchmark scenarios in parallel. In this paper, we measure and analyze the performance of Docker containers based on the running of TELEMAC modules. The expand of idea deploying simulations on Cloud platforms shows many benefits [24]. We have early experiences for running TELEMAC on Docker environment. The performance figures of TELEMAC on Docker highlight that Docker has many advantages in providing a lightweight computing infrastructure for Cloud.

# V. MODEL FOR DEPLOYING TELEMAC ON DOCKER CONTAINER

Docker containers like wrappers that can package applications and everything required for execution. For instances, inside a container, we can wrap a complete filesystem containing code, runtime, system tool and libraries. Docker uses a technology called Union file system (UnionFS) to provide

![](_page_3_Figure_6.png)

Fig. 2. The model of deploying TELEMAC on Docker.

the building blocks for containers. UnionFS is a filesystem service that allows files and directories of separate systems to be transparently overlaid, forming a single coherent file system [25]. In Docker, we can create various images, and they are read-only templates. Docker images include a series of layers. Thereby, UnionFS is used for merging these layers into a single image. In more detail, instead of replacing a whole image or entirely rebuilding with VM, we can update an application inside Docker container with a new layer gets build. Each Docker image is deployed on a base image, and multiple containers can use the same images without duplicating them. This is one of the reasons that makes Docker lightweight.

As Figure 2 shown, we propose a model for deploying HPC applications on Docker environment. The model use Docker container to merely create a running environment. Data are managed and configured under the host. For managing data in the container, Docker defines a definition named data volume to hold data. A data volume is a specially-designated directory within one or more containers that bypasses the UnionFS [5]. Data volume facilitate to persist data and make them independent of the container's life cycle. We employ these features to perform HPC applications. Data and related dependencies are located in the host machine. We mount a host directory into containers as a data volume. This benefits that data can be made available on any containers supporting the same applications. For HPC system, we consider Docker containers as the passive environment to submit jobs. All of configurations for execution are configured under the host. For example, we set up a computing infrastructure having InfiniBand network and Xeon-Phi co-processor that integrates with Docker container. From the model, we can guarantee data independent of running environment, and achieve the scalability of providing multiple users.

TELEMAC-MASCARET is a set of solvers for use in the field of simulating free-surface flows [1]. TELEMAC is written by Fortran language consisting of mathematics,

#### TABLE I OVERVIEW OF PERFORMANCE BETWEEN DOCKER AND VM.

|  |  |  | Performance Rate (%) |
| --- | --- | --- | --- |
| Criteria | Benchmark | Docker | VM |
| Latency of MPI send-receive on IB network | OSU-Benchmarks | 99.75 | 33.66 |
| Latency of MPI collective on IB network | OSU-Benchmarks | 92.12 | 44.32 |
| Computational capacity | High Performance Linpack | 91.88 | 81.5 |
| Ability of data access | Graph500 | 83.72 | 57.81 |

the physics, the advanced parallelization. To run TELEMAC on parallel system, there are three requirements including, parallel environment, source code of TELEMAC and precompiled library for parallel execution named METIS. The parallel environment has to provide the communication among compute nodes and the interface that allows two separate nodes to exchange data, e.g., Message Passing Interface (MPI). According to the model, we can configure and compile the source code of TELEMAC and related libraries under the host. Each container is merely the running environment containing the binaries of TELEMAC which are compiled under the host machine. This helps Docker diminish cumbersome. When Docker containers are used to run simulations, the input as well as data and TELEMAC source code can share among other containers and the host.

## VI. EXPERIMENTAL RESULTS AND ANALYSIS

We carry out our evaluation on the performance of Docker when running TELEMAC to simulate environmental issues such as salinization, flood inundation. We study the efficiency of Docker containers when performing real applications. In the previous research [18], we evaluate the performance of Docker and VM on criteria, namely network throughput, computational capacity and the ability of data access. Docker obtains more advantages than VM. For example, Table I shows our statistic about the efficiency of Docker and VM compared to PM. The values from Table I are the performance rate in comparison with PM. They are the ratio of Docker/VM performance results to PM results.

Following that, we use a real application to measure the efficiency between Docker and VM before providing a scalable computing infrastructure in Cloud. Firstly, we propose some scenarios with many sample simulation modules of TELEMAC from small scales to large scales. Secondly, we deploy real problems related to environmental issues that need to be simulated. For instance, the recent problem is the salinization in Vietnam's Mekong-Delta.

# *A. Testing environment*

Our evaluation environment considers the native performance as a standard to compare two virtualization platforms, namely Docker and VM. Objectively, we set up all VMs and containers on the given system called SuperNode.

The benchmarks are deployed on two compute nodes, equipped Intel Xeon CPU E5-2670 @ 2.6 GHz. There are 16 physical cores totally supporting Hyper Threading and 64 GB of RAM. The interconnection is 30 Gbps InfiniBand Connect-X3. The installed OS is CentOS 7 64-bit 3.10.0 on both of physical and virtual environment. In more detail, VMs and Docker containers are deployed by the latest version including QEMU 2.4.0.1/KVM and Docker 1.8.1 respectively. The problem sizes of our testbeds are equivalent to the capacity of the system under test. We focus on the execution time of Docker and VM when running TELEMAC for different modules.

# *B. Benchmarks*

*Parallelization and Speed-up:* In this scenario, we argue the meaning of parallelization and speed-up among Docker container, VM and PM in using TELEMAC for simulations. We deploy two VMs and Docker containers on each compute node. TELEMAC runs a problem that simulates a general flow with 100,000 elements in parallel mode. The problem is executed respectively on PM, VM and Docker. Time is a standard unit to evaluate the results of three environments.

Figure 3.a shows the execution time of simulation on three different platforms. The sequential execution is longer than parallel execution over 6 times as the best case of 32-core. Concretely, Docker obtains the performance that is slightly adjacent to the PM, while VM has a higher level of deviation. It is noticeable that the more cores the execution of HPC applications has, not the more efficiency the system achieves. Figure 3.b reveals that the case of using 30 cores gets the best performance. TELEMAC needs to consider the speedup of running simulations. The purpose of parallelization is to divide a single problem into multiple parts for solving. However, the more parts we divide, the more overhead we have to face. When we divide into too many parts for parallel computing, the number of messages exchanged will increase. That is one of reasons causing the reduction of performance. For the gain of deploying TELEMAC, Docker gets the rate of sequential time over parallel time being better than VM.

*Scalability and Availability:* We set up two scenarios to benchmark: the first one is the evaluation of PM, VM, Docker along with TELEMAC simulating different problem sizes from the small scale to the large scale. The second one is also the evaluation deployed on Docker and VM, but we run TELEMAC with the different amount of virtual instances. At the same time, each instance of VM or Docker performs an individual simulation. From these scenarios, we concern the changes of performance and overhead as well when running a huge range of different problem sizes, or deploying the execution environment on the scalable amount of virtual instances.

The main requirement of TELEMAC is the running time, and the shortest interval is the best. In TELEMAC system, one of the crucial factors affecting to the simulation is the amount of elements in the fine mesh. In detail, the simulated object is the flow of South China Sea. The fine mesh is built through refining the numbers of elements and nodes to simulate the features of flow. From Figure 4, although the problem sizes increase, the performance of Docker still keep the shorter execution time when comparing to VM. At the view of operation mechanism, the I/O communication of system is one

![](_page_5_Figure_0.png)

(a) Parallelism of simulation on PM, VM and Docker.

Fig. 3. Scenarios 1: TELEMAC running on distributed system.

![](_page_5_Figure_3.png)

![](_page_5_Figure_4.png)

of important problems. For VM, the operation of each VM is controlled by hypervisor layer. Therefor, the I/O virtualization of VM can make a large overhead with the increasing number of problem sizes. To perform the I/O functions, VM switches the context between VM-hypervisor and hypervisor-PM. When the simulation module of TELEMAC varies the problem sizes, the overhead of I/O control make the performance drop. For Docker, a benefit of its architecture is sharing resources with the host kernel. That makes the I/O access faster. This feature is one of the factors which creates the lightweight containers of Docker platform. Compared the results of Docker to PM, Figure 4 shows that the overhead of Docker can be acceptable with the demand of scalability.

Another scenario is the utilization of multiple users with

TABLE II THE SAMPLE EXAMPLES OF TELEMAC RUNNING ON DOCKER AND VM.

|  |  | Simulation modules |  |
| --- | --- | --- | --- |
| TELEMAC2D | TELEMAC3D | SYSIPHE | TOMAWAC |
| tide | tide | bump2d | bottom-friction |
| (Simulating the tide in 2D) | (Simulating the tide in 3D) | (Modeling the bump) | (Modeling the bottom friction) |
| m2wave | tidal-flats | bosse-t2d | dean |
| bowl | amr | foulness | fetch-limited |
| breach | bump | glissement | opposing-current |
| bridge | delwaq | bar-formation | shoal |
| bumpcri | depot | bifurcation | turning-wind |
| erosion-flume |  |  | whirl-current |
| estu-gir-3D |  |  |  |

different simulation modules on our system. In this case, we set up a series of simulation modules based on the sample examples of TELEMAC system. Table II shows the sample examples of simulation modules. The scenario generates the increasing number of VM/Docker instances, and each instance is considered as a user running TELEMAC. An instance performs a specific simulation module different from each other. For the hypervisor-based virtualization, the cost of managing VMs can rise sharply up with the increasing amount. Because, the hypervisor still causes the extra overhead for each workspace of VM without running jobs. In this scenario, the sharing architecture of Docker has more benefits. To provide the computing environment for a huge range of users, not all of instances occupy the resources continuously in a long time. This mechanism of Docker can get the efficiency in these situations because the allocation of resources is implemented at the same host kernel.

Figure 6 shows the means of execution time between Docker and VM with the different amounts of instances. For example, the value being 2 represents two VMs/Docker containers executing TELEMAC. For a variety of users accessing the system, the completion time of each instance is different. Some of VMs/containers can finish their task before others. Therefore, for the architecture of VM, a guest virtualized an entire

![](_page_6_Figure_0.png)

Fig. 5. The results of simulating Salinization and Flood Inundation.

![](_page_6_Figure_2.png)

Fig. 6. Execution time of VM and Docker when increasing the number of instances.

system from hardware to software can make the extra load for running. By contrast, Docker containers without running jobs would not generate the extra load. As the results of Figure 6 shown, Docker obtains the better performance figures in comparison to VM. Docker still keeps the efficiency with the increasing number of containers, and their overhead is nearly negligible. In each case of this scenario, one VM/Docker container solves one individual simulation modules shown at Table II. The benchmark scenario represents multiple users using TELEMAC simultaneously.

*Simulating the environmental issues in practice:* In this scenario, we evaluate the real values of performance and efficiency between Docker and VM. The existing problems are the environmental issues occurring in Vietnam. We use data and input of two issues to compare Docker to VM. The two issues include salinization and inundation in Southern of Vietnam, particularly in Ho Chi Minh city and Mekong Delta.

The first problem is salinization in Mekong Delta. This is the serious condition that has occurred only once in the last 90 years. About 971,200 hectares of farming area in eight provinces of the Mekong Delta has been affected by salt water, according to the Ministry of Agriculture and Rural Development. Especially, Ben Tre is one of the provinces that has severely affected by salinization. The suggested solution is using the numerical model of TELEMAC2D to simulate flows in the definite duration. After that, there are some methods in the field of civil engineering to tackle the problem. In terms of HPC system executing TELEMAC, a fine mesh is built up through refining the numbers of elements and nodes. In this case, the fine mesh contains 722,000 unstructured triangular elements, the largest and smallest edge of the mesh are 75 kilometers and 4 kilometers.

Similarly, the second problem is flood inundation. The state of floods, a vast plain, mainly in the northern part of the Mekong Delta, is affected by annual flooding overflows from Cambodia across the Vietnamese border. The flooded area ranges from 1.2 to 1.4 million hectares with the low and medium flooding, and around 1.9 million hectares with the high flooding annually. The fine mesh of this issue contains 716,000 triangular elements. The size of simulated area is 81,000 square kilometers. This problem is also used the numerical model of TELEMAC2D to simulate the state of floods.

Figure 7 shows the execution time of two issues mentioned above on PM, VM and Docker. The figures of PM are the standard to evaluate the efficiency of Docker and VM. From the Figure 7, it is clear that Docker takes the shorter time to run the simulations in comparison to VM. Docker has many advantages in terms of I/O access, lightweight architecture and resource allocation. The time of running real simulations on VMs takes 1.6 times longer than Docker containers. Figure 5 shows the results of simulating salinization and flood inundation in Vietnam by using TELEMAC2D. From these results, solutions can be proposed to deal with these problems.

![](_page_7_Figure_0.png)

Fig. 7. Evaluation of simulating the real environmental issues in Vietnam by deploying on PM, Docker and VM.

 

## VII. CONCLUSION AND FUTURE WORK

In this paper, we present a set of evaluations which aim to survey the performance as well as the efficiency of deploying TELEMAC on virtual platforms such as VM and Docker. Associated with the demand of parallel computing, this is the ability of providing the computing infrastructure for multiple users with different purposes that need to simulate the environmental issues. To keep up with these requirements, virtual platforms are the feasible solutions. In the previous works, we have done that deploying Docker on the advanced technologies, e.g., IB, Xeon-Phi co-processor. There are many good results about the performance of Docker in comparison to VM. Following that, this paper shows benchmarks and evaluations between Docker and VM when running the practical simulations by using TELEMAC. Based on the lightweight architecture, Docker has benefits of reducing overhead and remaining the execution time that is more efficiency than VM. We presented experiences for deploying TELEMAC on Docker environment. Our evaluation contributes a basic foundation to the trend that expands the computing environment of simulation applications on containers.

As a part of future work, we plan to develop a scheduling algorithm on Docker container. The algorithm aims to the allocation of resources for each container efficiently.

## ACKNOWLEDGMENT

This research was conducted within the "Studying and developing a 50-100 TFlops HPC system" funded by Department of Science and Technology - HCMC & HCMUT (under grant number 21/2015/H-SKHCN).

## REFERENCES

- [1] (2014) Telemac-mascaret homepage, the mathematically superior suite of solvers. [Online]. Available: http://www.opentelemac.org/
- [2] R. Issa, F. Decung, E. Razafindrakoto, E.-S. Lee, C. Moulinec, D. Latino, D. Violeau, and O. Boiteau, "Hpc for hydraulics and industrial environmental flow simulations," in *Parallel Computational Fluid Dynamics 2008*. Springer, 2010, pp. 377–387.
- [3] J.-M. Hervouet, "Telemac modelling system: an overview," *Hydrological Processes*, vol. 14, no. 13, pp. 2209–2210, 2000.
- [4] C. Boettiger, "An introduction to docker for reproducible research," ACM *SIGOPS Operating Systems Review*, vol. 49, no. 1, pp. 71–79, 2015.
- [5] (2014) Docker homepage. [Online]. Available: https://www.docker.com/
- [6] M. T. Chung, A. Le, Q.-H. Nguyen, D.-D. Nguyen, and N. Thoai, "Provision of docker and infiniband in high performance computing," 2016.
- [7] G. F. Pfister, "An introduction to the infiniband architecture," *High Performance Mass Storage and Parallel I/O*, vol. 42, pp. 617–632, 2001.
- [8] G. Chrysos, "Intel-R xeon phi coprocessor-the architecture," *Intel Whitepaper*, 2014.
- [9] Z. Shang, "High performance computing for flood simulation using telemac based on hybrid mpi/openmp parallel programming," *International Journal of Modeling, Simulation, and Scientific Computing*, vol. 5, no. 04, p. 1472001, 2014.
- [10] B. C. Pijanowski, A. Tayyebi, J. Doucette, B. K. Pekin, D. Braun, and J. Plourde, "A big data urban growth simulation at a national scale: configuring the gis and neural network based land transformation model to run in a high performance computing (hpc) environment," *Environmental Modelling & Software*, vol. 51, pp. 250–268, 2014.
- [11] P. Wittek and X. Rubio-Campillo, "Scalable agent-based modelling with cloud hpc resources for social simulations," in *Cloud Computing Technology and Science (CloudCom), 2012 IEEE 4th International Conference on*. IEEE, 2012, pp. 355–362.
- [12] E. M. Dow *et al.*, "The xen hypervisor," *INFORMIT, dated Apr*, vol. 10, 2008.
- [13] G. J. Popek and R. P. Goldberg, "Formal requirements for virtualizable third generation architectures," *Communications of the ACM*, vol. 17, no. 7, pp. 412–421, 1974.
- [14] A. Kivity, Y. Kamay, D. Laor, U. Lublin, and A. Liguori, "kvm: the linux virtual machine monitor," in *Proceedings of the Linux symposium*, vol. 1, 2007, pp. 225–230.
- [15] Q. Zhang, L. Cheng, and R. Boutaba, "Cloud computing: state-of-the-art and research challenges," *Journal of internet services and applications*, vol. 1, no. 1, pp. 7–18, 2010.
- [16] D. Merkel, "Docker: lightweight linux containers for consistent development and deployment," *Linux Journal*, vol. 2014, no. 239, p. 2, 2014.
- [17] F. Ghassemi, A. J. Jakeman, H. A. Nix *et al.*, *Salinisation of land and water resources: human causes, extent, management and case studies.* Cab International, 1995.
- [18] M. T. Chung, Q.-H. Nguyen, M.-T. Nguyen, and N. Thoai, "Using docker in high performance computing applications," in *Communications and Electronics (ICCE) (IEEE ICCE 2016), 2016 IEEE Sixth International Conference on*. IEEE, 2016, pp. 52–57.
- [19] C. MOULINEC, "Hpc evolution of the telemac system," in E*proceedings of the 36th IAHR World Congress, Hague, Netherlands*, 2015.
- [20] G. Merkuryeva, Y. Merkuryev, B. V. Sokolov, S. Potryasaev, V. A. Zelentsov, and A. Lektauers, "Advanced river flood monitoring, modelling and forecasting," *Journal of Computational Science*, vol. 10, pp. 77–85, 2015.
- [21] C. Villaret, J.-M. Hervouet, R. Kopmann, U. Merkel, and A. G. Davies, "Morphodynamic modeling using the telemac finite-element system," *Computers & Geosciences*, vol. 53, pp. 105–113, 2013.
- [22] R. Dua, A. R. Raja, and D. Kakadia, "Virtualization vs containerization to support paas," in *Cloud Engineering (IC2E), 2014 IEEE International Conference on*. IEEE, 2014, pp. 610–614.
- [23] W. Felter, A. Ferreira, R. Rajamony, and J. Rubio, "An updated performance comparison of virtual machines and linux containers," in *Performance Analysis of Systems and Software (ISPASS), 2015 IEEE International Symposium On*. IEEE, 2015, pp. 171–172.
- [24] W. Gentzsch, "Linux containers simplify engineering and scientific simulations in the cloud," in *Information and Computer Technology (GOCICT), 2014 Annual Global Online Conference on*. IEEE, 2014, pp. 22–26.
- [25] C. P. Wright and E. Zadok, "Kernel korner: unionfs: bringing filesystems together," *Linux Journal*, vol. 2004, no. 128, p. 8, 2004.

