# High Performance Systems: An Agent Based Application Power Profiling

H. V. Raghu1 , Ankit Kumar2 , Bindhumadhava Bapu S3 Real Time Systems and Smart Grid Group Centre for Development of Advanced Computing, 'C-DAC Knowledge Park', *Bangalore, INDIA*  raghuhv@cdac.in1 ,ankitk@cdac.in2 ,bindhu@cdac.in3

*Abstract—* **Power measurement and analysis are important aspects for optimizing the power consumption in High Performance Computing (HPC) systems. With the huge increase in the power consumption of HPC systems, it is important to compare systems with metrics based on performance per watt. There are various hardware and software based power measurement techniques available for HPC systems. But, it's a complex task to accurately measure and analyze the power consumption of entire HPC nodes in real time. Hence, we have used hardware based power measurement technique with Multi-Agent based framework for analyzing power in HPC systems at real time. We clearly demonstrated the power consumed while running the various workloads such as High Performance Linpack (HPL) and NAS Parallel Benchmarks (NPB).** 

#### *Keywords—Power Measurement; High Performance Computing; Multi-Agent Framework; HPC Standard Benchmarks.*

#### I. INTRODUCTION

 Over the past decade the HPC research community focused on improving only the performance. This lead to rapid improvement in the processor performance which resulted in increased power consumption of HPC systems. A supercomputer that appears on the Top500 list will consume Megawatts of electric power [1]. This in turn increases temperature, maintenance cost and the rate of failure. To overcome from this, the research on HPC power reduction is very much necessary. For the future HPC systems design power had become more important design constraint [2]. The following are the selected list of supercomputers from Top500 and its corresponding power requirements.

- K-Computer, RIKEN Advanced Institute for Computational Science, Japan,12.66 Megawatts [3].
- Titan Cray XK7, Oak Ridge National Laboratory, United States, 8.21 Megawatts [3].
- Sequoia BlueGene/Q, Lawrence Livermore National Laboratory, United States, 7.89 Megawatts [3].

 These supercomputers deliver the peak performance in petaflops, but the power required to deliver this performance is substantial. The statistical data shows that every 10 degree Celsius increase in temperature results in doubling the system failure rate, which reduces the reliability of the system [4]. These supercomputers are composed of hundreds of thousands or even millions of processing cores [5] with similar power consumption concerns [6]. Energy efficiency in these supercomputers is major concern not only because of cost reduction and failures, but also because these systems reaching the limits of power available to them.

 Understanding the accurate power consumption provides the first step to develop more effective control techniques. In this paper we will demonstrate how the power consumption can be measured for the various workloads using the hardware based measurement technique. Accurately measuring the power consumption of entire supercomputer with thousands of computing nodes is very complex task [1]. Hence, the hardware based power meter WattsUp? .NET is used to measure the power consumption of 4 nodes in a cluster. As an alternative we can connect each of the nodes with WattsUp? .NET power meter and the addition of the power consumption of all the nodes with network and I/O subsystem power will be the total system power consumption. The software based power measurement can be done by the utility developed by HP Integrated Lights-Out-3 (HP iLO-3). HP iLO-3 enables to view and control the power state of the server and the power meter provides the reading for 24 hour graphing of power and temperature data [7]. The power measurement is done for various standard HPC benchmarks on HP Proliant DL380 G7 Server (2xIntel Xeon 5600 series processor, 6 cores each, 4x8 GB RAM) with respect to resource usage and power impact on computing nodes. In Section II, related work in power measurement for identifying the Green500 list of supercomputers is given. In Section III, we will discuss the overview of agents and C-DAC Multi Agent Framework (CMAF). In Section IV, power measurement and analysis for HPC benchmarks using CMAF is discussed. Section V, we will explain the experimental set up and metrics for evaluating the power consumption based on hardware based measurement techniques for various HPC workloads. Our conclusions and future work are presented in Section VI.

#### II. RELATED WORK

There have been a numerous challenges and efforts to accurately measure and analyze power of HPC systems. For specific applications, majority of the researchers have focused on single node power consumption and extrapolated to the entire cluster by ignoring the network and I/O subsystem overhead. Basically there are many power profiling techniques available. Balaji and W. Feng had discussed about the power measurement implications and methodology in the Green500 list [14]. They also explained the real time power measurements on a single node and multi-node systems. James et al. [15] explained about measuring real power usage on High Performance Computing platforms and they described about the implementation of scalable power measurement framework that has enabled to examine real power use. R. Ge et al. [1] explained the power measurement tutorial for Green500 list and the measurement procedure for the single node compute system. In this paper we have measured the power for four nodes in cluster while executing Linpack and NAS benchmarks by using WattsUp? .NET power meter and the agents will collect power related information from the nodes in cluster. The CMAF framework will provide the agents an execution environment.

#### III. AGENTS AND CMAF

 A software agent is a program that acts on behalf of a user (e.g., travel agents, insurance agents). An agent has the following properties: Autonomy, Social ability, Reactivity, Proactive, Temporal continuity and Goal oriented [16]. An agent is a complete self-contained body of code, which physically moves from one computer to another. Before migrating, the agent stops execution at the source and resumes execution after reaching the destination. CMAF [17] is a network based application developed using Java and is based on the concept of data movement across the network. This framework addresses mobility, communication and various security issues of agents. The agents require an execution environment which is provided by the agent system, which runs on top of Java Virtual Machine.

 In CMAF, agent systems are classified into two categories - Real agent system (RAS) and Proxy agent system (PAS). The system related services are provided by system agents. These services include registry, communication, and user interface. These services provide various functionalities to the agent system. In a single network, there will be only one RAS and all the other agent systems are run as PAS. The PAS has lesser load compared to a RAS. RAS maintains a registry of all the agent systems running in the network whereas PAS does not. Agent execution starts from RAS and it can migrate to any PAS which is registered with the RAS.

#### IV. POWER MEASUREMENT AND ANALYSIS OF HIGH PERFORMANCE SYSTEMS USING CMAF

 We have used CMAF to profile standard HPC benchmarks with respect to resource usage (CPU, Memory, etc.) and power impact on individual computing nodes. The architecture of CMAF is shown in Fig. 1, where we used two agents named as Power Monitoring Agent (PMA) and Power Analyzing Agent (PAA).

PMA collects power and resource usage of all nodes. PAA is used to analyze the power statistics with respect to application behavior which is collected by PMA. As the initial setup, Real Agent System (RAS) of CMAF is installed on head node and all the compute nodes will be having Proxy Agent System (PAS). Whenever the head node and compute nodes turned on, these RAS and PAS will also be started for initiating the agents. Whenever an application is started from the head node, at the same time PMA will also be started. This agent will go to each compute node and collect the power readings using the WattsUp?.NET power meter and store the power consumption reading of all compute nodes on the power statistics repository which is situated at Head Node. These power consumption readings will be collected till the application is running. These readings can also be seen by administrator through a web application as shown in the Fig. 2 for various time intervals. Once the application is finished, the PAA will be started that will analyse these readings based on multiple run of the same application. Based on the analysis, PAA can take the intelligent decisions to optimize the power in the next run of the same application and the decision can be stored with the application behaviour in the knowledge base. So that next time same decision can be used if similar application comes for execution.

![](_page_1_Figure_8.png)

Figure 1. Power measurement and analysis using CMAF.

![](_page_2_Figure_0.png)

Figure 2. Power log information in CMAF.

Fig. 2 shows the web interface and the power data stored in the knowledge repository that is retrieved from the proxy agent system using WattsUp? .NET power meter.

![](_page_2_Figure_3.png)

Figure 3. Power measurement of a cluster.

### V. EXPERIMENTAL SETUP

## A. *Metrics for Power Efficiency Evaluation*

The Metrics are essential for us to accurately measure and thereby evaluate the efficiency of power consumption and useful for decision making [10]. While the metrics for assessing performance has got considerable attention over the past decade and the assessment of power efficiency have received comparably less attention [2]. Identifying a single objective metric for energy efficiency in supercomputers is a difficult task [1,8,9]. The Green500 list uses "Performance Per Watt" (PPW) as the metric to rank the Energy Efficiency (EE) of supercomputers. The performance per watt metric is defined as [1] :

#### *Performance* PPW

*Watt*

- Performance is defined as the achieved maximal performance by the Linpack benchmark on the entire system.
- Power is defined as the average power consumption during the execution of Linpack benchmark.

$$E E_{i}={\frac{P e r f o r m a n c e_{i}}{P o w e r C o n s u m e d_{i}}}$$

The energy efficiency is calculated while executing different benchmarks in the cluster, where each i represents the different benchmark tests.

#### B. *Profiling power consumption*

Power management requires the power usage patterns of the target system to be captured accurately. Various power profiling techniques available are using simulations, analytical modeling, direct online power consumption measurement, monitoring based power consumption analysis, power behaviour sampling and software instrumentation [10]. The scope of this paper is to explain the power measurement by using direct online power consumption measurement and to store the data in the knowledge repository using CMAF that helps in taking intelligent decisions for optimizing power.

 The direct online power measurement will have additional power measurement tools to measure and record power consumption at run time [11]. In this experiment we use WattsUp? .NET as a device to measure the power consumption of four HP Proliant DL380 G7 servers, each having two Intel Xeon E5645 processors with six cores. These four systems are clustered using PBS resource manager and Maui scheduler. Each CPU core has maximum frequency of 2.4GHz and minimum of 1.6 GHz. Each node has RHEL 6.2 operating system and MPI version MPICH2-1.4.1. WattsUp?.NET meter displays the consumption in Watts, Watt-hours, Volts and Amps in one second interval for a particular period of time specified by the user. The output data from the meter is saved in memory of the device or it can be logged to the remote computer via USB interface. Fig. 3 illustrates the power measurement for four nodes in a cluster and the data logging using the remote computer.

 The WattsUp? .NET power meter has to be connected between power supply AC input of the selected cluster node and the socket connected to the external supply. The data from the power meter has been logged in the remote system and it can be downloaded to a Windows or Linux machine. In the next step, we have installed several standard HPC benchmarks such as High Performance Linpack(HPL) and NAS Parallel Benchmarks(NPB) in HP Proliant servers for our experiment. Here we will analyse the power consumption of the node with respect to the CPU utilization and memory utilization.

 The software based power measurement is done by the utility provided by HP Integrated Lights Out (HPiLO-3). HPiLO provides different ways to configure, update and operate HP Proliant servers remotely. We have chosen to use HPiLO using scripts and command line instructions. The scripting tools provide a method to check the power consumption and configure multiple iLO systems and to control servers. Using scripting tools, we can :

- Control the server power states. The various states are HP dynamic power saving mode, HP static low power mode, HP static high performance mode, OS control mode.
- Retrieve power consumption data.
- Issue various configuration and control commands.

 We are using SMASH CLP scripting language. It provides a set of commands for configuration and control of servers. On iLO-3, SMASH CLP scripts will be accessed through the Secure Shell (SSH) port. The power settings command enable to view and modify power settings. We embedded SMASH CLP commands inside shell scripts and login to the iLO port using SSH.

#### C. *Power Profiles*

In order to have a better understanding of the power consumption of applications we first profile the power consumption of the cluster when it is idle. The power consumption of any application/benchmark can be determined by:

$$P_{A}=P_{T}-P_{I}$$

where,

PA is the power consumption by the application.

PT is the total system power consumption while executing the application.

# PI is the power consumption when the system is idle.

Hence it is necessary to identify the idle system power consumption with respect to CPU utilization and Memory utilization. Fig. 4 illustrates the power consumption of 4 node cluster when it is idle. The power consumption will be in the range of 485 to 495 watts and the average memory utilization is approximately 7 percent and the average CPU utilization is less than 1 percent.

![](_page_3_Figure_18.png)

Figure 4. Power consumption of the cluster when it is idle.

Fig. 5 illustrates the power consumption of 4 node cluster during the execution of Linpack benchmark with respect to average CPU and memory utilization. High Performance Linpack (HPL) benchmark measures the floating point rate of execution for solving a linear system of equations [12] which increases the CPU utilization. The time to execute Linpack benchmark varies depending on the input problem size.

![](_page_4_Figure_0.png)

Figure 5. Power profile for Linpack benchmark in 4 node cluster.

For multi-processor scientific applications we used NAS Parallel Benchmarks (NPB). These are a small set of programs designed to help and evaluate the performance of parallel supercomputers. The benchmarks are derived from computational fluid dynamics applications and consist of five kernels (IS,EP,MG,CG,FT) and three pseudo-applications (BT,SP,LU) [13] . NPB problem sizes are predefined and indicated as different classes. We have executed NPB for class-B problem size. The experimentation is done for 64 processors of BT,CG and FT benchmarks. The corresponding CPU utilization, Memory utilization and power consumption of BT,CG and FT benchmarks are shown in Fig. 6-11.

![](_page_4_Figure_3.png)

Figure 6. CPU utilization and Power Consumption of BT benchmark for 4 nodes in a cluster.

![](_page_4_Figure_5.png)

Figure 7. Memory utilization and Power Consumption of BT benchmark for 4 nodes in a cluster.

Fig. 6 represents CPU utilization and power consumption of Block Tri-diagonal (BT) benchmark and Fig. 7 represents memory utilization and power consumption of BT benchmark for 4 nodes in a cluster. BT solves a synthetic system of nonlinear Partial Differential Equations using three different algorithms involving block tri-diagonal, scalar penta-diagonal and symmetric successive over-relaxation solver kernels, respectively.

![](_page_4_Figure_8.png)

Figure 8. CPU utilization and Power Consumption of CG benchmark for 4 nodes in a cluster.

![](_page_5_Figure_0.png)

Figure 9. Memory utilization and Power Consumption of CG benchmark for 4 nodes in a cluster.

Fig. 8 represents CPU utilization and power consumption of Conjugate Gradient (CG) benchmark and Fig. 9 represents memory utilization and power consumption of CG benchmark for 4 nodes in a cluster. CG estimates the smallest Eigen value of a large sparse symmetric positive-definite matrix using the inverse iteration with the conjugate gradient method as a subroutine for solving systems of linear equations.

![](_page_5_Figure_3.png)

Figure 10. CPU utilization and Power Consumption of FT benchmark for 4 nodes in a cluster.

Fig. 10 represents CPU utilization and power consumption of Fourier Transform (FT) benchmark and Fig. 11 represents memory utilization and power consumption of FT benchmark for 4 nodes in a cluster. FT solves a three-dimensional partial differential equation using the Fast Fourier Transform.

![](_page_5_Figure_6.png)

Figure 11. Memory utilization and Power Consumption of FT benchmark for 4 nodes in a cluster.

The profiling of the application is done with respect to resource utilization (CPU, Memory) and power consumption. The utilization of CPU and memory varies significantly across various nodes. Even though CPU and memory are idle for substantial time intervals, but it still consumes a large amount of power. This data can be used to investigate better power management and resource management strategies which leads to further power optimization. The analysis of various HPC benchmarks/applications helps to estimate which resource are essential for specific application and which resource can dynamically be in low power/idle state.

#### VI. CONCLUSIONS AND FUTURE WORK

In this paper, we present the technique for power profiling of four nodes in the cluster for MPI based standard HPC benchmarks such as High Performance Linpack and NAS Parallel Benchmarks using WattsUp? .NET power meter. C-DAC Multi Agent Framework is used to retrieve the power consumption and resource utilization data from the nodes. The power measurement can also be done to single node in cluster and can be extrapolated to the number of nodes that are available considering network and I/O subsystems overhead. As an alternative we can also connect each of the nodes with WattsUp?. NET power meter. We have analyzed the power consumption of the node in accordance with the CPU utilization and memory utilization.

In future, our technique will be extended to measure, analyze and optimize power for real HPC applications in large heterogeneous cluster. The power measurement will also be done in various subsystem levels like CPU, memory, network, disk etc. Application level power will also be determined for further power optimization.

#### ACKNOWLEDGMENT

We would like to thank R.K.Senthil Kumar, Bhavyasree Unni, Sumit Kumar Saurav, Manisha Chauhan, Nazia Parveen and B.Jayanth for their support and valuable help while conducting this research.

#### REFERENCES

- [1] R. Ge, X. Feng, H. Pyla, K. Cameron, and W. Feng, "Power measurement tutorial for the Green500 List," June 27, 2007.
- [2] S. Kamil, J. Shelf, and E. Strohmaier, "Power efficiency in High Performance Computing," Lawrence Berkeley National Laboratory, Berkeley, International Parallel & Distributed Processing symposium, 2008.
- [3] Top500 Supercomputers [Online]. Available : http://www.top500.org/ list/2011/11/100, [Accessed: May-2012].
- [4] I. Rodero, S. Chandra, M. Parashar, R. Muralidhar, H. Seshadri, S. Poole, "Investigating the Potential of Application-Centric Aggressive Power Management for HPC Workloads," 17th IEEE International Conference on High Performance Computing (HiPC)-2010, Goa, India, December 2010.
- [5] J. Dean, "Large-scale distributed systems at Google: current systems and future directions," in 3rd ACM SIGOPS International Workshop on Large Scale Distributed Systems and Middleware,2009.
- [6] "Mission possible-greening the HPC data center," HPC Wire,2009.
- [7] "HP Integrity iLO-3 Operations Guide," Edition-4,June 2011.
- [8] C. Hsu, W. Feng, and J. Archuleta, "Towards efficient supercomputing: A quest for the right metric," 1 st IEEE Workshop on High-Performance, Power-Aware Computing, 2005.

- [9] S. Sharma, C. Hsu, and W. Feng, "Making a case for a Green500 List," 2 nd IEEE Workshop on High-Performance, Power-Aware Computing, 2006.
- [10] Y. Liu and H. Zhu, "A survey of the research on Power Management Techniques for High Performance Systems," Software : Practice and Experience, Volume 40, Issue 11, October 2010.
- [11] J. Flinn and M. Satyanarayanan "Powerscope : A tool for profiling the energy usage of mobile applications," Proceedings of the 2nd IEEE Workshop on Mobile Computing Systems and Applications(WMCSA'99).New Orleans, Louisiana,USA, Feb 1999
- [12] HPC Challenge Benchmark [Online]. Available : http://icl.cs.utk. edu/hpcc/, [Accessed: May-2012].
- [13] NAS Parallel Benchmarks[Online], Available: http://www.nas.nasa. gov/publications/npb.html,[Accessed: May-2012].
- [14] B. Subramaniam and W. Feng, "Understanding Power Measurement implications in the Green500 List," IEEE/ACM International Conference on Green Computing and Communications, 2010.
- [15] J. Laros, K. Pedretti, S. Kelly, J. Vandyke, K. Ferreira, C. Vaughan, and M. Swan, "Topics on Measuring Real Power Usage on High Performance Computing Platforms," IEEE International Conference on Cluster Computing, 2009.
- [16] Lange and Oshima, "Seven Advantages of agent mobility," CPS 720 Artificial Intelligence Topics with Agents, http://www.ryerson.ca/ ~dgrimsha/courses/cps720/mobilityadvantage.html.
- [17] S.Venkatesh, B. S. Bindhumadhava and A. A. Bhandari, "Implementation of automated Grid software management tool: A Mobile Agent based approach," Proc. of Int'l Conf on Information and Knowledge Engineering, June 2006, pages 208-214.

