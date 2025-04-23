# Power, Performance And Thermal Management Using Hardware Performance Counters

Balvinder Pal Singh Intel India P Ltd, IIIT-B Research Scholar balvinder.singh@iiitb.org; balvinder.pal.singh@intel.com

*Abstract***—CPU Performance, Voltage and Temperature are the primary design constraints for the high compute systems today. With increased demands of high compute and processing capabilities, there is a need to measure and optimize system power requirements wherever possible. Modern Operating systems provide efficient resource managers but those are not working at a lower level and rather are more generic in behavior. Though the chipsets and Operating Systems are providing various techniques like DVFS (Dynamic Voltage and Frequency Scaling), DPM (Dynamic Power Management) but these are generic approaches to power management and agnostic to the use-case impact. System level power management must consider the variable nature of the use case and the effect of environment rather than just applying a single rule to save power. In the way it is also supposed to detect quickly and apply an apt technique based on situation and given environment. Temperature plays a vital role apart from the CPU status during the high compute processing. Thermal management must be taken care before taking an overall decision and not just the processing demands from the peripherals. This paper presents a mechanism where the Hardware Performance Monitoring Counters (PMC) to be used to empirically, yet accurately represent the dynamic power situation in given environment. Results in this paper suggests CPU being the main heat producer and within the CPU Microarchitecture the heat can be empirically co-related to overall power and temperature read during the use case. Cache miss to hit ratio, dram speeds and bus speed are also the contributors of overall CPU heat**

*Keywords— Power Consumption, Power Management, Linux performance Events, Multicore Processing, High performance computing (HPC), Power, Voltage and Temperature (PVT), Datacenter power, Power optimization, Energy Efficiency, Performance Monitoring Counters (PMC), Dynamic Power management (DPM), Dynamic Voltage and Frequency Scaling (DVFS), Advanced Configuration and Power Interface Specification (ACPI)* 

# I. **INTRODUCTION**

Power consumption has become a major concern for all High power computational (HPC) [1] devices today. With the inclusion of mobile devices with high speeds, multicore environment to do a lot of background and foreground activities, the Operating systems and underlying processing units are under high pressure to deliver the output in short time leading to high rate of battery drain. On the server side, the problem is even more serious as, the server systems must rely on mechanical and conventional cooling methods which are leads to heavy expenses and high logistics to keep the servers cool. Modern computing and communication devices support multiple power management techniques like Dynamic Power Management (DPM) and Dynamic Voltage and Frequency Scaling (DVFS) [2, 3] to provide a reduction of the currents at system level. These deal with the selective suspension/slowdown of the hardware components that are not being used or are remaining idle for some time and the system detects that there is a chance to sleep for some specified duration to save overall power. Component temperature is proportional to power dissipated and power is proportional to the voltage squared. As a result, voltage scaling using accurate *DVFS* techniques will be very

 Prof. B Thangaraju IIIT, Bangalore, India b.thangaraju@iiitb.ac.in

effective power control strategy of the Digital Baseband ICs, Microprocessors/Controllers on the board and typically the DPM is beneficial for peripherals like the disk drives, network interfaces and others connected on the Main processor. These techniques can be considered as a control knobs to have a processing and thermal mitigation of the CPU and the peripherals.

 

DPM, DVFS and Hardware Performance counters are specific to given architectural design. In general, there is a common behavior amongst many CPU architectures in terms of power management and hardware counters (PMCs), such as the AMD Phenom 9500, AMD Opteron 8212 or Intel Core i3/5/7/9, Pentium, Atom, Xeon, Sandy Bridge, Broadwell, Haswell, Skylake, Others [5]. Conventional power management delve deep into the physical measurement of power during a use case in the lab using the physical power meters connected to the several components and at an overall supply level. This method may help for lab measurements, not in the real field. In real field, where devices and applications go into the hands of millions and billions of users, it becomes difficult to carry out every measurement with the probes and with the wires pulled out to the power meter. In this situation a smart selection of performance counters turns out to be good way to get closer to the problem. Processors have come up with several performance counters embedded into the hardware itself so that a certain level of debug capability could be exercised by using these counters. Ranking important counters, amongst several other available counters remains the key – for instance there could be a set of counters studied for understanding say a malicious user application which is trying to access specific CPU and Memory in a stressed and malicious manner. In another example understanding how these counters could be used for applications to maintain Lip-Sync between the audio and video frames during video playback. In this situation two or more counters would come from two or more processors. In this example first processor may be a digital signal processor (DSP), running the audio/video encoder/decoder – providing samples to the peripheral, while the second processor may be the main application processor doing Media streaming. These processors have a high chance of going out of sync since they are running at different clocks leading to a drift between audio and video frames. Relevant performance counters will provide a corrective measure to remove such sync delays. Another example is power dissipation use-cases, the counters could be chosen as a set to reflect the Memory, CPU behavior during the higher power analysis. Other than performance counters, core CPU and socket temperature are important vector and acts as an index of power dissipation analysis. Modern devices have a lot of temperature sensors installed spatially at several locations on the board and can be used to provide such a heuristic. Installing several temperature sensors and then taking actions to reduce temperature is a crude way and not scalable for all platforms. This approach is not a recommended for the board designs due to several inaccuracies and latencies in the sensor-based model of the real hotspot in the entire board.

This paper suggests an alternate approach of using Hardware Performance Counters, to achieve a scalable and much more efficient model of calculating power within CPU, Memories and I/O's. Another goal of the paper is to propose a model to create a co-relation of Counters to the overall Power and proposes a way to control the fan and the voltage using counters instead of physical sensors and applying DVFS blindly across the cores. This may mean that the Operating system to be applying the DVFS based on the counter thresholds, and as per the new policy that enables more CPU time

# 978-1-7281-6828-9/20/$31.00 ©2020 IEEE

and the schedule bandwidth to the time-critical jobs. A new method is also proposed in this paper called "Fine DVFS" which can be applied over counters rather than the crude and slow sensors. This may be beneficial to operate within the thermal bounds without reducing the performance. Section II defines the problem statement and methods to achieve cooling, Section III and IV provides experimental report of worst-case scenario and a method to calculate power using performance counters, instead of using the hardware sensors.

# II. **METHODOLOGY**

Be it computing on an individual hardware in a smaller scale like an individual Personal computing device or Warehouse scale computing power dissipation is a persistent problem [6]. It is graver an issue in the data center where the split of power usage at a supply levels are 61% CPUs and 18% DRAMs. Power and cooling overheads together counts 10% of the overall power requirements to work. Increase in CPU cores, threads and increase in the processing speeds would further push the amounts of power utilized in the CPUs and memories. In summary, close to 90% of the power drainage is in the processing, memory accesses and I/O. Remaining energy goes into mitigating thermal impacts.

# **III. THERMAL IMPACT TO THE POWER/PERFORMANCE**

 One important vector effecting semiconductor performance is temperature of the cores on the CPU/Memory slots. There have been several efforts from software side for example in, *Chandra Mohan et.al.* [7] proposed to have schedulers designed with temperature awareness in design. Temperature increase has an adverse effect on the carrier mobility and the switching speeds of the transistors in the circuits. Due to higher temperatures, there could be several ill effects to the semiconductors (due to electromigration) on a permanent basis sometimes. For the power sensitive devices, the heat generation must be controlled, but under the heavy requirement from the applications when the performance is demanded from the overall system, CPU cores and Memory I/O would be at its peak during the span of serving. This leads to thermal thresholds to hit and then power manager to kick-in and try cooling down the cores. This leads to performance loss and wastage of power every time the cores and slots hit to maximum thresholds before being cooled down. *Rajarhsi et al.*  [12] proposes to make temperature profiles of the sub-module at the time of synthesis itself and make sure the "hot spot" formations are catered at design time itself. This may reduce the component hotspots to some extent but still the preventive actions have to come into play only at run time.

Another situation, where CPU cores are heterogeneous (different cores with different speeds and power requirements), the processing/thermal efficiency becomes hard to control as there may be a very low priority task may be running in the CPU which is running at a high speed and hogging it, while the higher priority one is running on CPUs with low speed. Application awareness and scheduling are independent tasks and if linked, will pose a problem to the overall thermal and processing behavior. The need is to run a low-level hardware based power and thermal engine to monitor and correct power dissipation at a more generic level. Independent lowlevel techniques like monitoring Performance Events or hardware counters may work well on localized zones. Published report highlights for example [9] software-based optimization techniques are not efficient enough for thermal issues. Operating Systems could help controlling things at more generic level, not at the hardware granularity level, as the high-level software power management techniques are not aware of data and environment available at the hardware level which could make a difference in evaluation. It bases itself on doing prediction of temperature and apply DVFS knob based on prediction based on the heuristics. Based on the data received from the environment/sensors and performance-counters, corresponding actions are proposed to be taken. As shown in Figure 1, the proposal is to apply 1) DVFS/DPM techniques, 2) Modulate Fan speeds based on temperature 3) Applying selective suspension of certain hardware blocks, that are heating up (a.k.a. Hot-Spots). These actions would act as the control knobs to read the feedback again and then apply corrections, learn and then apply knobs again. In some of the modern computational systems, there are fans over the processor or the hot-spots to reduce the temperature by in-direct interventions. Note this acts as one of the knobs but fan itself would be running on the batteries and would consume additional power by itself. So only controlling the thermal conditions using the external cooling techniques may not be a preferred option.

![](_page_1_Figure_7.png)

**Figure 1: Knobs & Actuators for Power Heuristics** 

# IV. **THERMAL ZONE AND COOLING**

On a platform thermal Zone [10] is defined as conceptual area containing the execution hardware, thermal sensors and its own cooling controls. Partitioning based on the thermal zones make the overall assessment of the power and thermal constraints more efficient. Individual controls enable fine-tuned control of a particular "hot-spot" on the hardware proves better in performance balancing with other specific cores/subsystems as these modules may still have a higher thermal headroom [6]. Increased thermal headroom enables selective cores running at higher clocking even when the hotspot is identified and is being optimized. This way is more efficient than applying DVFS to all the cores and reducing the frequency/voltage to curb the performance of the whole system. Cooling policies may be defined as *Active, Passive & Critical (Figure 2). A*ctive policy would involve direct actions like the increase of the fan speeds to reduce temperatures, Passive policies would apply throttling of the processing on the thermal zones based on the controls available on given platform(s). Critical trip points are where the power manager within say Linux or Windows operating system would selectively/completely shut down the device(s) or even the entire system in situations where the thermal conditions are critical and may harm the system if kept running.

![](_page_1_Figure_11.png)

**Figure 2: Active, Passive, Critical Thresholds - Example** 

Active cooling as shown in Figure 3 is direct method of controlling fan's speed by modulating (increasing or reducing) fan speeds based on a pre-defined table (also dynamically configurable via *Advanced Configuration and Power Interface Specification*  (ACPI) [10]).

![](_page_1_Figure_14.png)

**Figure 3: Active Cooling (Linux Example) – Fan Speed Vs Temp** 

It takes the fan speed to a pre-defined level per the pulse applied. ACPI provides the APIs for the Power manager to control the cooling policies. Active cooling allows system to still work at a higher or programmed processing by extending the thermal envelope until core or the subsystems reach their critical temperature. Relying only on the active cooling has two downsides – noise creation and fan power consumption. Passive cooling is an indirect technique for cooling. Experiments on Linux Operating System's power manager takes to reduce the thermal conditions and is generally at the cost of using throttling the cores on peak performance. There is a direct impact of applying existing indirect approach as it dips the overall system performance. This may not be acceptable in some use-cases where low latencies are priority over power-saving like a Gaming use case. Dynamic voltage scaling and Dynamic Frequency Scaling are used by power manager's governing policies as passive cooling mechanisms and are described in experimental section of this article.

 Critical trip points may occur in the devices during a long term and loaded use of operations, even after the available Active & Passive cooling mechanisms are applied. Under this situation, the power manager on hitting the thermal threshold may take a call to move the system into lower power states like S4(Hibernate) or S5(Off) depending on the options programmed where it will cut the clock completely of the system and let it cool. These are called critical trip points and are essential to safeguard the hardware sustenance.

# A. *CPU Microarchitecture*

Many of the earlier works stated the use of several temperature sensors, at many places of the board [13] but this is not a feasible design as keeping so many sensors are not just impact on the cost of the design but also is a crude design to solve a problem. Other issue with sensor could be due to being localized to a place and being inaccurate/missing the hot spots which are close by. One of the elegant and more accurate solution is to have Hardware counters published to reflect the internal states of the hardware. Performance counters being the hardware counters are generally known to have no impacts on the performance itself. *Rafia et.al.* [14] bring out the fact of perf counters being non-intrusive becomes ideal for carrying out critical measurements which are sensitive otherwise.

PMCs are surely the right way to go ahead given an area to solve an issue – for example to solve the security, power, performance, or even thermal profiling of a design. Another advantage of this approach is that it is accurate and very close to the real hardware conditions. Almost all the modern computing devices are coming equipped with hundreds of performance counters, for the debug and evaluation purposes, the key lies in choosing the right registers to evaluate a problem. In [4] *Goel et.all.* suggests a ranking rule based on experimental models to select following CPU PMC classes to rank and weight them for power dissipation evaluation for example: FP Units, Memory/Cache, Stalls and Instructions Retired. The first and second level caches are generally very fast to access and in some of processors like the Pentium 6 [5], the Level 2 caches are also inside the chip on the same die as processor. Figure 4 defines a typical cache positions in a sample Microprocessor. This is again architecture dependent and has a major impact in Processor Power dissipation.

![](_page_2_Figure_5.png)

#### **Figure 4: Processor Sample Microarchitecture**

Putting the level 2 cache inside the processor, helps further reduction in the access latencies. It not only reduces power but also balances difference in speeds between the memory and processor speeds and to remove fetch latencies. Some of the latest processors from all manufacturers have a L3 cache to balance system bus latencies and allows better power efficiency. Figure 5 provides a sample on-die L1-I, L1-D and L2, L3 memory depths. The microarchitecture described for example for the P6 families can do decode, dispatch and complete execution for three instructions in one clock cycle. To further handle the instruction throughputs, a 12-stage pipeline is present that supports out-of-order instruction execution as well.

| Architecture: | ×86 64 | Architecture: | ×86 64 |
| --- | --- | --- | --- |
| CPU (s) : | র্ব | CPU (s) : | 8 |
| On-line CPU(s) list: 0-3 |  | On-line CPU(s) list: 0-7 |  |
| Thread (s) per core: | 2 | Thread (s) per core: | 2 |
| Core (s) per socket: | 2 | Core (s) per socket: | ਖ |
| Socket (s) : | 1 | Socket (s) : | 1 |
| Model name: | i5-6200U CPU @ 2.30GHz | Model name: | i5-8265U CPU @ 1.60GHz |
| CPU MHz: | 508.449 | CPU MHz: | 800.006 |
| CPU max MHz : | 2800.0000 | CPU max MHz: | 3900.0000 |
| CPU min MHz: | 400.0000 | CPU min MHz: | 400.0000 |
| L1d cache: | 32K | Lld cache: | 32K |
| Lli cache: | 32K | Lli cache: | 32K |
| L2 cache: | 256K | L2 cache: | 256K |
| L3 cache: | 3072K | L3 cache: | 6144K |

**Figure 5: Microarchitecture details of example two processor variants** 

# B. *Ranking of Counters for Power Co-relation*

Under higher speeds of access, it becomes important to avoid wasteful cycles and keep the processor working on the efficient tasks. Cache latencies may lead to wasteful cycles being running on the CPU. Parameters like "Number of Cache Misses per instruction executed" is an important indicator of the waste ratio. The more the processor must work to get information first time from the cache, the more energy it drains. To evaluate such an indicator with counters becomes the key, as the sensors or even the power meters won't reach to this cause unless there is a count of all misses, stalls, latencies are quantitatively represented. Tracking "*Instructions Retired"* along with their types, allows to follow *FPU Vs Integer Unit operations*, "*L1 Misses (Instruction and Data) & L2 misses"* are a direct indicator of *wasteful expense* of power per execution cycle. Tracking *"Total instructions retired"* provides *performance and power sense*.

Referring Table 1 as ideal Power Idle situation, for an 8 core, single package CPU – the Temperature of each core starts from 37oC on an average at the CPU Load of less than 1%. Fan has not started at this temperature.

| Core/ | Temp | Frequency | CPU Utils | Power | Fan RPM |
| --- | --- | --- | --- | --- | --- |
| Package | ( oC) | (MHz) | (%age) | (Watts) |  |
| 0 | 36 | 900.1 | 0.9 | PKG - 0.9 W Core 0.3W | 0 RPM |
| 1 | 37 | 900.3 | 2.4 |  |  |
| 2 | 35 | 970.4 | 0.9 |  |  |
| 3 | 36 | 915.1 | 0.9 |  |  |
| 4 | 36 | 900.2 | 0.9 | Uncore 0.0 W |  |
| 5 | 37 | 900 | 0 | DRAM 0.2 |  |
| 6 | 37 | 963 | 0 | W |  |
| 7 | 36 | 981 | 0 |  |  |
| Average | 37 | 928.76 | 0.7 |  |  |

#### **Table 1: Performance Matrix Under CPU Idle Situation – Governor policy – "Powersave"**

As per Figure 3, fan starts at MINTEMP threshold, 45oC in the device under test. Fan speed keeps on increasing linearly along with the temperature of the CPU Socket and reaches for example MAX threshold of 4200 RPM at around 80oC. Power at the overall Package level can be considered as under 1W in the given IDLE conditions. Linux power manager policies are kept in "*Powersave*" mode for all practical considerations. This paper doesn't consider the "Hot-spots" and controlling them per-se on the thermal trigger but provides a means of co-relating CPU Performance counters to empirically evaluate an average thermal condition. Real values of system parameters are considered, and a co-relation is derived using some key set of Performance counters specifically addressing the power as a vector is discussed in the next section.

# V. **EXPERIMENTAL MODEL**

In this paper experimental model takes the assumptions for the measurement for Linux OS based power manager to be running at the nominal "*Power Save mode"* rather than "*Performance Mode".* In Figure 6, "*Power Save" Mode,* the CPU cores would go into the lower C states where-ever possible thereby saving power in the real situation. Power save mode allows the CPU Core's frequencies to go up or down based on the load requirements and comes to the "*Nominal Mode*" when the load is minimal. The change in frequency happens in steps via the scaling factor on the Linux Operating System's power manager.

| +++ Processor |
| --- |
| CPU model = Intel(R) Core (TM) i5-8265U CPU @ 1.60GHz |
| /sys/devices/system/cpu/cpu0/cpufreq/scaling driver = intel pstate |
| /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor = Powersave |
| /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governor = performance, powersave |
| /sys/devices/system/cpu/cpu0/cpufreq/scaling min freq = 400000 [kHz] |
| /sys/devices/system/cpu/cpu0/cpufreq/scaling max freq = 3900000 [kHz] |
| /sys/devices/system/cpu/cpufreq/energy performance preference = balance performance |
| /sys/devices/system/cpu/cpu0/cpufreq/energy performance available preferences = default |
| performance balance performance balance power power power |

#### **Figure 6: Linux Power Manager Configuration**

In *Performance mode*, the CPUs would keep running into the highest frequency most of the times to avail the best performance from all 8 cores. Here the intension is to achieve the best user experience and not power. In this mode the temperature of the loaded cores would be high and power dissipation will also be high compared to the scaled power-save mode. For experiments the configuration taken is an 8 core CPU, running Linux 2.6 kernel supporting both the powersave and performance modes for all the 8 cores. Packed in single package, consists of *8 cores, 2 threads of execution each with L1d and L1i caches of 32KB each, L2 cache of 256K and L3 of about 6MB cache.* Power configuration options available for experiments are both power save and the performance modes. Experiments will include stressing the system with load on CPU processing, memory, mathematical operations like the square root operations and the I/O to and from the DDR memory.

# VI. **EXPERIMENTS – LOAD DESCRIPTION**

Under the idle conditions, in each system, the Operating system based on the governor settings and load at that given time, will choose a clock speed as shown in Figure 7 "*CPU frequencies (all cores)".*  Since the power save mode is selected as a *"scaling governor"* settings, the CPUs are working at nominal and lower frequencies under 1GHz.

| PARAMETERS | CO | CI | C2 | C3 | C4 | CS | CE | C7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Temp [C] | 38 | ਤੇਰੇ | ਤੇਰੇ | 38 | 38 | ਤੇਰੇ | ਤਰੇ | 38 |
| Freq [MHz] | 954.7 | ਰੇ 20 | 916.7 | 918.2 | 914 5 | 900.1 | 900.1 | 902 |
| CPU Util (%) | 1.4 | 0.5 | 0.5 | 3.8 | 0.5 | 0 | 0 | 1.4 |
| Power (W) | Core Power: 0.3, Uncore = 0, Dram 0.2 |  |  |  |  |  |  |  |
| Fan Speed | Fan Off, this will kick off at the specified package threshold |  |  |  |  |  |  |  |
| (sensor) | temperature |  |  |  |  |  |  |  |

**Figure 7: Detailed Breakup of Per Core Temp, Freq, Fan Speed, CPU Utilization and Core/Uncore Power (W)** [IDLE and Power Save governor settings] – Sampled every 2 seconds for example

This has a direct co-relation to the Power it drains in various pipelines, memories and internal caches etc. Table #1 provides a snapshot of one such capture with Average Temperatures around 37oC, sub 1GHz average CPU speeds, and power at package levels of just under 1Watt, Core 0.3W, Uncore 0.0 W, DRAM 0.2 W.

When under the loaded conditions the following loads described in Table 2, were applied to the experiment under various vectors as load type using the sample application from the user space.

| Component | Linux Test Vector Description |
| --- | --- |
| CPU | 8 Worker threads spawned to do some intensive operation on the CPU, keeping the ALU and FPU |
| busy along with Cache operations |  |
| I/O | 8 Worker threads swanned to load the Internal |
|  | Memory I/O Operations (RAM) – leading to the |
| I/O activity with DRAM. |  |
| MEM | Doing Malloc and Free operations on the Memory |
| manager, keeping the DRAM operations |  |
| EXT I/O | Using writes on the External Memory/HDD with |
|  | heavy constant load – should increase the Uncore |
| power. |  |
| ALL | Combination of all the stress types together to |
| simulate a typical general end user scenario. |  |

#### **Table 2: Contributors to the Overall Power Dissipation**

 "ALL" Use case of *Table 3* measures the Uncore and DRAM power dissipations as very low, as compared to the overall Core or package power is < 5% for DRAM compared to Core Power and as low as 0.3% for Uncore compared to the Core Power requirements. The Core is the main source of Power dissipation followed by DRAM access and then the external I/O's. So, finding Core power and temperature accurately is the key to take actions in given time restrictions.

| Load type | Options (Peak |  |  | Average Performance Results |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | load) | Tem | Freq | Util | Watts* | Fan |
|  |  | p(C) | (G) | (%) | (C/DR/UC) | (RPM) |
| CPU | #Cores loaded | 93 | 3.7 | 100 | 38.2/0.4/0.4 | 4222 |
| I/O | #I/O threads | 45 | 0.9 | 19 | 2.9/0.2/0 | 2515 |
| ME M | #Mem Writes | 51 | 1.8 | 100 | 7.2/1.6/0 | 2550 |
| Ext I/O | #HDD Writes | 66 | 3.1 | 14 | 11.6/0.6/0.7 | 3521 |
| ALL | Together | 87 | 3.1 | 100 | 32/1.6/0.1 | 3444 |

# **Table 3: Performance Matrix Under Max Load – Governor policy "Powersave", C/DR/UC* Core/DRAM/Uncore power (W)**

# **VII. LATENCY IN TRIGGERING COOLING AND APPLYING DVFS**

During the experiments, and as also highlighted in some of the earlier works [14], the overall method of using temperature sensors is proved to be slow in responding to apply cooling mechanisms either DVFS/DFS or Fan control (other Active/Passive cooling methods). Figure 8 shows a snapshot in sequence measured Capturing Core temperatures of each core and socket are ~96oC and CPU Utilization for all cores 100% with almost max clock hit. This data is coming from the CPU usage obtained from the Linux OS, and real sensors for temperature and fan speeds.

![](_page_4_Figure_0.png)

# **Figure 8: CPU Temperature at 96**oC **- load test – 8 cores and the Package level**

Under such heavy load there is still a good amount of latency seen to kick the fan and the other control knobs. The fan speeds were still low at about 2545 RPMs and as a result in Figure 9 it can be seen that the *Critical temperature* had been reached due to exhausting the thermal headroom. Under this case the CPU speeds were dropped drastically to 2263 MHz thereby reducing the performance by about a third ratio. This situation can be offset by making use of the Heurisitcs which can be developed based on the accurate Hardware Perfromance counters rather than using the sensors [11] and controlling the mechanical equipments to lower the temperatures. There can be efficient mechanisms and more accurate to rather avoid the critical threholds being hit rather than lowering the overall performance abrubtly.

![](_page_4_Figure_3.png)

# **Figure 9: Real Measurement of CPU Load, Power, Fan Speed and Temperature at peak load**

Techniques like the DVFS and DPM may be effective in throttling the CPU and the Peripheral performances respectively by lowering the frequency of operation and by reducing also the voltage steps of the peripheral as needed. Doing this will increase the leakage currents since the CPU and the Peripherals would take more time to do the same job and hence would be kept active on the clock for a longer duration. On the other hand, if such throttling's would not be applied the system would exhaust the thermal headroom and would be forcefully shut to lower power states forcefully upon hitting the critical temperatures. So, the thermal headroom is the ceiling that the circuit must take care. Figure 9 provides peak values at a given load for all 8 cores. It is observed that the CPU remains 100% loaded (all cores), Wattage close to 35W, Temperature reaching the critical threshold and as the Fan kicks in the temperature drops by about 20- 25oC which allows applications to still run with full performance mode. CPU remains the most significant consumer of the power whereas DRAM and other Uncore contributions are low. Performance counters are like the hardware registers that the chips may provide and there are many such counters that help qualitatively evaluate and model a prediction based on the current values and the historical data. This paper is not dealing with predictions, it tries to derive an approximate co-relation to the PVT Situation based on some chosen performance counters within the Multicore CPUs. Performance counters acts as a soft sensor implanted in all the thermal zones

# **VIII. INTERNAL PERFORMANCE COUNTERS FOR CPU**

Counters like the Instructions retired, Instruction per cycle, Frequencies in relations with Nominal Frequencies, L2/L3 Misses and L2/L3 Misses per instruction are some of the key consumers for the indicative power dissipation. In terms of thermal zones, as referred in several works [2, 5] suggest that most heated areas out of the ones described in Figure 10 are the Floating point and integer point executive (Floor map referred from [13]) – FpExe, IntExe, L2 Branch Prediction Unit (BPU).

![](_page_4_Figure_9.png)

**Figure 10: Floor-map of the Sample CPU** 

These could be used for the generation of the PVT models with certain levels of accuracy. Sample PMCs are provided in the Table 4 are read from the Processor side in a poll interval of about 20ms for all calculations. Calculation method for the counters is similar to one mentioned by *Fernando et. al*. [8]. Method to calculate the HW Performance counter is as below

- a) Read the Chip version
- b) Find the relevant counters supported
- \ c) If Support availble, start polling (at 20ms freq)
- d) Calculations delta from last readings for L2Cache miss, calculate the delta from last read and represent in a right scale or a ratio.
- e) Start the load and stress test and capture counters
- f) Repeat every 20ms.

#### *Table 4 Legend*

*INST/Nominal Cycle=Num of instructions executed/Nominal INST/Cycle= Number of instructions executed per current cycle. FREQ= Ratio if Operating frequency to Nominal Frequency.* 

- *L3Miss = Number of L3 Misses X 10-6,*
- *L2Miss = Number of L2 Misses X 10-6.*

*L3Hit = Number of L3 Hits out of 1(hits + misses assumed 1). L3M/INSTR = Number of L3 Misses per executed instruction.* 

- *L2M/INSTR = Number of L2 Misses per executed instruction. READ is the Gigabytes read from the main memory controller. WRITE is the Gigabytes written to the main memory controller*
![](_page_4_Figure_24.png)

| INST/ | INST/ | FREQ/ |  |  | L3M/ | L2M/ |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NOM CYCLE | CYCLE | NOM |  | L3MISS L2MISS L3HIT | INSTR | INST |  | READ(GB) WRITE (GB) # INST |  |
| 1.16 | 0.896 | 1.29 | 0.661 | 2.19 | 0.624 0.000158 0.000523 |  | 0.842 | 1.13 | 4.19E+03 |
| 1.81 | 0.881 | 2.05 | 0.944 | 2.96 | 0.583 0.000145 0.000454 |  | 1.22 | 1.78 | 6.51E+03 |
| 1.89 | 0.923 | 2.05 | 2.27 | 4.49 | 0.42 0.000332 0.000657 |  | 1.56 | 1.49 | 6.83E+03 |
| 1.78 | 0.868 | 2.05 | 1.14 | 2.96 | 0.531 0.000177 0.000461 |  | 1.36 | 1.77 | 6.42E+03 |
| 1.73 | 0.842 | 2.05 | 1.6 | 3.98 | 0.51 0.000256 0.000638 |  | 1.55 | 1.68 | 6.24E+03 |
| 1.63 | 0.793 | 2.05 | 1.5 | 3.88 | 0.529 0.000255 0.000659 |  | 1.52 | 1.74 | 5.90E+03 |
| 1.75 | 0.854 | 2.05 | 1.52 | 3.79 | 0.517 0.000238 | 0.00059 | 1.47 | 1.77 | 6.42E+03 |
| 1.72 | 0.841 | 2.05 | 1.39 | 3.5 | 0.515 0.000221 0.000559 |  | 1.45 | 1.8 | 6.27E+03 |
| 1.87 | 0.91 | 2.05 | 1.31 | 3.27 | 0.517 0.000194 0.000485 |  | 1.41 | 1.74 | 6.73E+03 |
| 1.61 | 0.785 | 2.05 | 1.59 | 3.97 | 0.506 0.000274 0.000684 |  | 1.58 | 1.65 | 5.81E+03 |
| 1.53 | 0.746 | 2.05 | 1.25 | 3.17 | 0.51 0.000226 0.000572 |  | 1.42 | 1.8 | 5.53E+03 |

**Table 4: Sample Performance L2/L3/I/O/INSTR details (units explained above the table)** 

This research work considers Cache performances Vs Power and Temperature using counters. Then this is compared with the measured power and Temperature graphs (as in Figure 9) and attempt to propose a co-relation between the real measurement Vs PMC counter-based measurements are proposed. *Reza Zamani et al.* [15] reported that the correlation of the coefficients of mapped top 25 counters and based on the data ranked "*Data Cache access, Dispatch stalls, dram hit miss conflicts, and Cache block commands"* to be ranked for power modeling. This paper leverages Cache performances criteria based on all evaluated ranks for important counters. To calculate the total Power consumption assuming a frequency would be governed by the access speed of individual subsystems, number of times that resource or the vector has been accessed.

# IX. **MATHEMATICAL MODELLING**

Several literatures have referred to power models, in [18] Dayarathna et.all have provided "Additive server energy models", "System Utilization based server energy models" and others, we present the simplistic additive energy model where the addition of the Power from various contributing modules are being considered.

# I. **POWER ESTIMATES (ADDITIVE ENERGY MODEL)**

1) Power Vectors to be defined as "Vp" consists of

$P_{Total}=P_{Core}+P_{DRAM}+P_{Uncore}+P_{Others}$

$$P_{\it Core}\sim P_{\it L}\it Rate+P_{\it L}\it BH_{\it H}+P_{\it L}\it2M_{\it S}+P_{\it L}\it3M_{\it S}+P_{\it F}\it3M_{\it S}+P_{\it F}\it+P_{\it IP+}\it P_{\it others}\...\tag{2}$$

For each of the subcomponents inside "*PCore "component access* time and the scaling factor remains the key. Access times to be calculated by the following equation for each vector –

_AccT${}_{v}$ - NumberOfAccess/AverageAccSpeed......... (3)_

2) Power Vectors to be defined as "Vp" consists of

$V_{p}\equiv$ _[L2Miss, L3Miss, L3Hit, Stalls, Float-point, Int-Point]_

3) Average Access Speed (cycles/s) for all vectors "Vp" consists of

_Asp${}_{v}\equiv$ [Asp${}_{L2}$Miss, Asp${}_{L3}$Miss, Asp${}_{L3}$Hits, Asp${}_{L3}$As Sp${}_{L4}$-pout, Asp${}_{L4}$-pout]_

_Polar_

4) Scaling factor (Power-weights) for all vectors "Vp" consists of

Sfv ≡ *[SfL2Miss, SfL3Miss, SfL3Hit, SfStalls, SfFloat-point, SfInt-Point] ... (5)* 

5) Total Number of Counters for each "Vp" consists of … (6)

PCv ≡ *[PCL2Miss, PCL3Miss, PCL3Hit, PCStalls, PCFloat-point, PCInt-Point]* 

6) Collecting these 6 equations, Pcore can be inferred as below –

$$P_{C o r e}\sim\sum\nolimits_{j=1}^{n s a m p l e s}\sum\nolimits_{i=1}^{v}(P C v(i,j)/A s p v(i,j))*S f v(i,j))\tag{7}$$

7) Putting Eq 7 back into Eq 1

$$P_{Total}=P_{IDLE}+\sum_{j=1}^{\#samples}\sum_{i=1}^{v}(PCv(i,j)/Aspv(i,j))*$$ $$Sfv(i,j))+P_{DRAM}+P_{Uncore}+P_{Others}\tag{8}$$

For all practical computations the Uncore, DRAM power dissipations are < 5% variance compared to the Core Power dissipating for the core loaded case. *Equation #8* evaluates overall power that the Model would have once running for a given time. This could be averaged over time and assuming the Frequency steps to be linear the model calculations could be made. A linear regression is proposed to be applied on the Model, over this factor as per all previous works [4, 13]. For the accuracy the scaling factor could be defined from the practical values on a given platform.

Scaling Factor highly depends on the platform architecture and would vary and to be derived separately for each given CPU architecture. Vector "*POthers"* in *Equation 1* consists of the factor of Temperature as well in the given platform. At higher temperatures, the Fan and other cooling systems should also be considered as the power drain elements and as the temperature increases this dissipation would increase in a Linear fashion as per Figure 3 (Temperature Vs Fan Speeds)*. PIDLE* can be directly calculated as per "Table 1: Performance Matrix Under CPU Idle Situation" (~0.9 Watts average in this case).

# II. **"FINE DVFS" - A NEW AVOIDANCE MECHANISM**

Based on the mathematical model, one of the goals of this paper is to propose a change in the Operating system's frequency scaling evaluation and method to move to the very fine scaling steps *(call "Fine DVFS"*). To read and calculate the power based on the model instead of reading temperature from the sensors. The counters could be polled or better set on the event-based triggers to the operating systems. Upon reception of the threshold trigger per CPU, a decision is to be taken by the Operating system based on the demand and priority of the use case. The thresholds to be kept based on the predictive pattern and to alert the system well before the trigger is set to happen, for an early action on the thermal upper limit is reached as per Figure 3 (where the active/passive cooling gets kicked in)

- Define fine grained frequency scaling steps rather than coarse ones that are used today
- OS to be able to detect the event-trigger say 10% below the power threshold, at which the power manager would take short steps to control Frequency at fine steps while still managing the performance and Estimated Power
- Apply fine DVFS steps and observe the selected counters along with overall estimated power range
- Delay kicking in active/passive cooling (fan) as long as Estimated Power is controlled with *"fine DVFS"*
- Remove dependency on the hardware sensors for DVFS– as it is not just expensive/non-localized. Once the model accuracy is proved with counters, the temperature sensors could even be thought of being removed from the circuit.

# **III. RESULTS**

Performance Counters collected and plotted against the Power and Temperature waveforms. Results shows clear and direct corelation between the Performance counters for CACHE Performances, with the CPU Frequency ratio to Nominal. Figure 11 and 12 provides the L2, L3 Cache Misses. In papers [4][13] *Goel et.all and Jong Sung et.all* have professed use of linear regression to find the coefficient and slope of PCMs Vs actual temperature measurements. This provides a good empirical correlation between the sampled counter values and actual temperature values.

![](_page_5_Figure_33.png)

### **Figure 11: L2/L3 Cache Performance Vs Time (PMC)**

The PMC based method not just allows the reading of the temperature and power values empirically but also allows to create a model which is free from any physical sensors. This method also helps in removing the latency in taking an action as explained in section III-B. The conventional method shows that the active and passive cooling were too delayed due to the physical latencies of sensors and even also depends on the physical proximity of the sensors on the board. Dependency on sensor may not be met of the hotspot lies farther on the board compared to the sensor placement. Given the limitation on the number of sensors available on the board, a Temperature aware DVFS can be applied using the PMC. This would be accurate and reduce the hitting of critical cutoffs as the temperatures of the hotspots may hit ~100oC in no time based on load. Usage of performance counters as a decision maker for the actions for thermal mitigation is much more efficient as it will allow much quick and accurate triggers. It will also enable taking pinpointed and selective actions like localized actions or selective module suspension.

Figure 12 and 13 incudes the Counter based readings including the instructions retired as a function of CPU Speeds, Temperature and Power. These correlates very closely in the given active timeframe *(38:10.8 to 38:22:9)* with the Figure 9 which are the real readings done from the Linux Operating System's CPU and Sensor updates.

![](_page_6_Figure_2.png)

**Figure 12: Instructions Retired (Scaled to fit), Temp, Power and Cache Miss Performance (PMC)** 

![](_page_6_Figure_4.png)

#### **Figure 13: Ratio of Frequency to Nominal, Power and Cache Miss Performance (PMC)**

# X. **CONCLUSION**

Performance Monitoring Counters open a great world of data analysis not just in the power monitoring and analytics, but also in the world of Security, throughput, Stability of a product and many other Key Performance Indicators. It has an immense potential to allow the Learnings applied to the data that is available directly from the hardware. This paper provides a co-relation between the Actual values of temperature and Important PCM counters during a worstcase scenario. Paper also suggests in the mathematical model how the overall power can be calculated as a function of PCM Counters and Temperature.

# XI. **REFERENCES**

- [1] Roberto Gioiosa, Sally A. McKee, Mateo Valero- Designing OS for HPC Applications: Scheduling - 2010 IEEE International Conference on Cluster Computing
- [2] K.Skadron, M. Stan, K. Sankaranarayana, W. Huang, S. Velusamy, and D.Tarjan, "Temperature-Aware Microarchitecture: Modeling and Implementation," ACM Trans. Architecture and Code Optimization, vol.1,no.1,pp.94-125, Mar. 2004
- [3] J.Srinivasan and S.V. Adve, "Predictive Dynamic Thermal Management for Multimedia Applications," Proc. 17th Int'l Conf. Supercomputing (ICS), June2003
- [4] Bhavishya Goel*, Sally A. McKee, Roberto Gioiosat, Karan Singh, Maor Bhadauria, and Marco Cesati - Portable, Scalable, per-Core
- [5] Intel® 64 and IA-32 Architectures Software Developer's Manual Volume 3B: System Programming Guide, Part 2 [Chapter 18 – Performance Counters]
- [6] Luis A. Barroso, Urs H, Parthasarthy R, Book "The Datacenter as Computer – designing warehouse scale machine – third edition
- [7] Chandra Mohan Velpula, Jayant, Vishal Shahi CPU Temperature Aware SAcheduling - 978-1-4799-8792-4/15/2015 IEEE
- [8] Fernando G. Tinetti, Mariano Mendez An Automated Approach to Hardware Performance Monitoring Counters - 2014 International Conference on Computational Science and Computational Intelligence 978-1-4799-3010-4/14©2014IEEE
- [9] David Brooks, Margaret Martonosi, Dynamic Thermal Management for High-Performance Microprocessors - *Proceedings of the 7th International Symposium on HighPerformance Computer Architecture, Monterrey, Mexico, January 2001*
- [10] Advanced Configuration and Power Interface Specification https://www.intel.com/content/dam/www/public/us/en/documents/arti cles/acpi-config-power-interface-spec.pdf
- [11] S.W. Chung and K. Skadron, "Using On-Chip Event Counters for HighResolution, Real-Time Temperature Measurements," Proc. IEEE/ASME 10th Intersoc. Conf. Thermal and Thermomechanical Phenomena in Electronic Systems(ITHERM), June 2006.
- [12] Rajarshi Mukherjee, Seda Ogrenci Memik, and Gokhan Memik Temperature-Aware Resource Allocation and Bindingin High-Level Synthesis , DAC June 2005, California, USA, ACM 1-59593-058-2/- 5/0006
- [13] Jong Sung Lee, Kevin Skadron, Sung Woo Chung- Predictive Temperature-Aware DVFS – IEEE Transaction on Computers – 2010
- [14] Rafia Inam, Mikel Sjodin, Markus Jagemar, Bandwidth Measurement using Performance Counters for Predictable Multicore Software - 978- 1-4673-4737-2/12 ©2012 IEEE
- [15] Reza Zamani and Ahmad Afsahi, A Study of Hardware Performance Monitoring Counter Selection in Power Modeling of Computing Systems – International Green Computing Conference – 2012
- [16] Xin Liu, Li Shen.Cheng Qian,Zhiying Wang Dynamic Power Estimation with Hardware Performance Counters Support on Multicore Platform- Communications in Computer and Information Science book series (CCIS, volume 451) – 2014
- [17] Rance Rodrigues, Arunachalam Annamalai, Israel Koren and Sandip Kundu, - Dynamic Power Estimation with Hardware Performance Counters Support on Multi-core Platform - IEEE TRANSACTIONS ON CIRCUIT AND SYSTEMS-I
- [18] Data Center Energy Consumption Modeling: A Survey, Miyuru Dayarathna, Yonggang Wen, Senior Member, IEEE, and Rui Fan, IEEE COMMUNICATIONS SURVEYS & TUTORIALS, VOL. 18, NO. 1, FIRST QUARTER 2016

