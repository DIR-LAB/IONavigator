# **Chiplets Integrated Solution with FO-EB Package in HPC and Networking Application**

Po Yuan (James) Su*, David Ho, Jacy Pu, Yu Po Wang

Siliconware Precision Industries Co. Ltd. (SPIL)

No. 123, Sec 3, Chung Shan Rd., Tantzu, Taichung, Taiwan * E-mail: Jamessu@spil.com.tw; Tel: 886-4-25341525 ext. 5075

*Abstract*—Since its introduction in the 1960s, high performance computing (HPC) has made enormous contribution to scientific, engineering and industrial competitiveness as well as other goverment missions. High data rate with high speed transmission has been required for networking and high performance computing application, the chip size and package design has been become larger and larger. Accompanied by the big size design with package, the physical limits has the high cost for the advanced silicon node. The demand for higher functionality devices drives integration technologies to overcome limitations in Moore's Law. Heterogeneous integration is the one of technologies to meet high performance computing application standards using high bandwidth and Input/Output (I/O) density. The split die of integration in package is the best solution to increase gross die with wafer good yield rate for cost efficiency, and Fan-out Embedded Bridge (FO-EB) Package would be the best representative for HPC and Networking application.

 The FO-EB is meaning spilt dies with embedded bridge die in fan out package which Inter Connect Die (ICD) become silicon bridge die to do the communications for high electrical performance purpose. Comparing with 2.5D package and FO-MCM package, FO-EB package warpage not only close with 2.5D package, but also better than FO-MCM (Fan-out Multi Chip Module) package. Besides, the electrical performance for high bandwidth memory as good as 2.5D package and FO-MCM package. The FO-EB package has integrated silicon ICD which means provide interconnections between spilt dies with short distance and the package model is more flexable than 2.5D package. That is why FO-EB would be the better choice for HPC and Networking application.

The reason we choose FO-EB because it can contribute the same electrical performance to 2.5D package with FO-MCM package and the package warpgae well to be controlled. In this paper, we like to discuss a designed to evaluate the FO-EB and do the measurement comparsion for the warpage, and do the electrical preformance comparsion for the 2.5D, FO-EB and FO-MCM packages. Finally, this paper will find out the chiplets Integrated solution with FO-EB Package in HPC and Networking Application.

Key words: *High Performance Computing (HPC), Input/Output (I/O), Fan-out Embedded Bridge (FO-EB), Fanout Multi Chip Module (FO-MCM), Inter Connect Die (ICD)*

# **I. INTRODUCTION**

Fan Out Packages are the popular packages in many different applications. FO-EB Package can provide the ideal solution for high I/O, high electrical performance demand in where high frequency, high speed are required. By using chiplets with fine-trace ICD technologies to achieve package high performance requirement. In the past, Intel's manufacturing philosophy was known as 'Tick-Tock' Model and each generation would alternate between the two, allowing Intel to take advantage of a familiar design on a new process node, or using a mature node to enable a new performance-focused design. The computing power of the CPU doubles every 18 months, and now that silicon chips are approaching the limits of physical and economic costs. Now, Moore's Law is approaching failure [1]. There is a technology gap between Moore's Law and data rate speed transmission and product applications are outpacing Moore's law. In terms of solving this issue, we will need higher performance processors to recover the technology gap. Refer to Figure 1 for Technology Gap

![](_page_0_Figure_11.png)

Now, Heterogeneous Integration technologies have received growing attention for a mainstream interconnection solution in the semiconductor assembly field due to their ability to achieve increasing device functionality and package miniaturization. The technology is also related to next generation of high performance semiconductor package structures such as chiplets integration or some complex designs. Therefore, there are a lot of different demands for advanced packages and technologies from semiconductor industry. In this industry, the next focus growing opportunity market would be the HPC application in the near future.

Today, the social media is evolution such as Facebook transform to Meta, this change has not only make software better but also hardware resource support. Based on the hardware, there are several ways can enhance the processor performance, and chiplets integrated should be the most efficiency for this [2]. This advanced technology had used chiplets integration form factor with high performance system solution for networking applications. In this paper, the advanced FO-EB package not only can reduced the most of Coefficient of Thermal Expansion (CTE) mismatch but also provide the good electrical performance as well as 2.5D and FO-MCM packages. That is the reason FO-EB Package would be the best representative for HPC and Networking application. To compare we would Refer to Table 1 for Comparison of Different Design Structure.

| Item |  | 2.5D | FO-EB | FO-MCM |
| --- | --- | --- | --- | --- |
| Schematic |  |  |  |  |
| Structure | Interconnection | Si Interposer | Si Inter Connect Die + Organic RDL | Organic RDL |
| Warpage |  | ★ | *** | ★★ |
| Performance | Chip Module Stress | ★★ | *** | ★★★ |
| Electric |  | ★★ | ★★ず | *** |
| Overall Ranking |  | ★ | ★★★ | ★★ |

Table 1. Comparison of Different Design Structure

 The FO-EB structure was studied and demonstrated on the 70*80mm package size. For HPC, the major requirement is high speed performance and this portion can be used accelerate graphics with high band width memory, refer to Figure 2 for the FO-EB Product Structure.

![](_page_1_Picture_5.png)

Figure 2. FO-EB for HPC Product Structure

### **II. HBM ELECTRICAL PERFORMANCE VERFITY**

In terms of the HPC and Network requirements that higher bandwidth is the one of the major key, and high bandwidth memory can play this role to achieve the high volume of data transmission. There is the comparison table for electrical performance between FO Packages, 2.5D Package and HBM2E. The HBM2E request working voltage is 480 mV, and FO-EB shows 662 mV and FO-MCM shows 1013 mV, and 2.5D shows 600 mV that means these 2 FO Packages and 2.5D Package all been acceptable to use HBM2E. All of Eye Diagrams show the Width and Height all clear and can be contribute good electrical performance and all Eye Diagrams show that FO-MCM Package is better than FO-EB Package because the FO-MCM RDL line width and line space design is larger than FO-EB. FO-EB Package shows better than 2.5D Package. The RDL line width design larger and the performance will be better, However, FO-EB is another good choose for the electric performance [4] [5]. Refer to the Table 2. PKG Electric Performance for HBM Demand. In this paper, the FO-EB TV with 6*6mm ICD was applied between on Die and HBM of the bottom side for this test vehicle.

|  | PKG Electric Performance for HBM2E |  |  |
| --- | --- | --- | --- |
| Item | FO-EB | FO-MCM | 2.5D |
| W(um)/ S(um) | 0.5/1.5 | 2/3 | 0.5/0.5 |
| HBM2E (3.2Gbps) Eye Diagram |  |  |  |
| HBM2E Request (mV) |  | 480 |  |
| Height (mV) | 662 | 1013 | 600 |
| Width (ps) | 294 | 301 | 288 |
| Result | Accept | Accept | Accept |

Table 2. PKG Electric Performance for HBM Demand

## **III. MODULE STRESS SIMULATION**

There is the overall Module Stress simulation comparison for different structure interconnection which to compare with 2.5D, FO-EB and FO-MCM Packages. To compare with these three packages that we can see FO-EB has the best module stress than 2.5D and FO-MCM packages. Refer to the Table 3. Module Stress Simulation.

|  |  |  |  | *More stars = Better |
| --- | --- | --- | --- | --- |
| Item |  | 2.5D | FO-EB | FO-MCM |
| Schematic |  |  |  |  |
| Structure Interconnection |  | Si Interposer | Si Inter Connect Die + Organic RDL | Organic RDL |
| Module Stress | Die Corner | 1.6X | 1X | 1.4X |
| RDL Bending |  | No RDL | 1X | 1.9X |

Table 3. Module Stress Simulation

The first one item is Die Corner Stress comparison with 2.5D, FO-EB and FO-MCM. Each of the point to represent one chip module size, and there are 3 different color for different packages that 2.5D use blue color, FO-MCM use pink color and FO-EB use green color. For 2.5D, Silicon Interposer is the connection between chips and substrate, and the die corner stress shows 1.6X bigger than FO-MCM stress 1.4X and FO-EB stress 1X. We can also see the FO-MCM versus FO-EB, both of trends show FO-EB die corner stress smaller than FO-MCM. We can see the trend with die corners that 2.5D Silicon Interposer has the biggest die corner stress than FO-MCM and FO-EB and FO-EB has the smallest corner stress than 2.5D and FO-MCM packages. FO-EB would be the best one die corner stress than other two packages. Shown as Figure 3. Die Corner Stress.

![](_page_2_Figure_3.png)

There are two groups A and B with different package and module sizes that we to do the module stress simulation and warpage shadow moiré refer to the Table 4. Packages Warpage Comparison

![](_page_2_Figure_5.png)

The second one item is RDL Bending Stress comparison with FO-EB and FO-MCM. Each of the point to represent one chip module size, and there are 2 different color for different packages that FO-MCM use pink color and FO-EB use green color. For FO-MCM, the RDL bending stress versus FO-EB, both of trends show FO-EB die corner stress smaller than FO-MCM. We can see the trend with RDL bending stress that FO-MCM ratio 1.9X has bigger stress than FO-EB 1X which means FO-EB has the smallest corner stress than FO-MCM package. Shown as Figure 4. RDL Bending Stress.

![](_page_2_Figure_7.png)

Table 4. Packages Warpage Comparison

 We do the same package size of die corner stress for group A 2.5D with FO-EB and group B FO-MCM with FO-EB , and we already know the FO-EB has the best die corner stress performance than FO-MCM and 2.5D. And the FO-EB still has the lowest RDL bending stress than FO-MCM. The next one is the package warpage moiré for A, and 2.5D use the orange color and FO-EB use blue color to present warpage moiré from room temperature to high temperature, and the result shows FO-EB has better warpage performance than 2.5D at 260ć. Refer to Figure 5. FO-EB versus 2.5D Warpage.

![](_page_3_Figure_0.png)

Figure 5. FO-EB versus 2.5D Warpage

The last one is the package warpage moiré for B, and FO-MCM use the orange color and FO-EB use blue color to present warpage moiré from room temperature to high temperature, and the result shows FO-EB has more stable warpage than FO-MCM. Refer to Figure 6. FO-EB versus FO-MCM Warpage.

![](_page_3_Figure_3.png)

![](_page_3_Figure_4.png)

In fact, there are some warpage mismatch that we need to overcome by engineering. First at all, the most often is the chip module and substrate attach become package. Typically, the chip module attach to the substrate and the chip module usually has warpage either smile or cry, and your substrate should make it cry or smile during the process. If substrate and chip module opposite, it become high risk such as bump bridged or nonwetting issue.

Accompanied by larger chip module size, the FO-EB has lowest die corner stress than 2.5D silicon interposer and lowest RDL stress than FO-MCM. That's the advantages why FO-EB would be the best representative for HPC and Networking application.

### **IV. WARPAGE PERFORMANCE**

To meet with the high integration requirement, all resistor, inductor and capacitor of components be put into assembly. This is a chiplet integration and module approach comparing with 2.5D TSI assembly methodology to reduce the space during actual product design stage. There is a key challenge for this paper is warpage performance with FO-EB, 2.5D and FO-MCM structures and we need to consider the structure balance of warpage result. The purpose of this TV is to determine the warpage performance after package process. The Shadow Moiré methodology as shown in Figure 7. Shadow Moiré was measured by white light through a reference grating on surface of sample with temperature heating, and recorded warpage shadow data by camera [6].

![](_page_3_Figure_10.png)

Figure 7. Shadow Moiré of Warpage Measurement

# **V. TEST VEHICLE DESCRIPTION**

In this paper, the test vehicles (TV) was designed with advanced FO-EB technology to see the warpage and reliability data for the 70*80mm FO-EB TV demonstration.

To verify the package quality purpose that the TV FO-EB to demonstrate the real package and package size is 70*80mm and this TV build two FO chip modules and do the warpage measurement, reliability and verification test as well. Refer to the Table 5. FO-EB TV Structure

![](_page_4_Figure_0.png)

Table 5. FO-EB TV Structure

# **VI. RELIABILITY TEST PLAN**

The reliability test plan with MSL4, TCJ 3000 Cycles, u-HUST 264 Hours and HTSL1000 Hours [5]. The plan also put the SAT inspection and O/S test. See the Figure 8. Reliability and Verification Test Plan.

![](_page_4_Figure_4.png)

Figure 8. Reliability and Verification Test Plan

The package level warpage performance by using Shadow Moiré measurement result shown in Figure 9. The package warpage meet the TCJ criteria result (Room temperature to High temperature). According to signed warpage chart result, this TV is within JEDEC warpage requirement (Max. 380um). Based on warpage requirement point of view, the FO-EB structure meet warpage requirement.

![](_page_4_Figure_7.png)

Figure 9. Shadow Moiré warpage data comparison

### **VII. RESULTS**

First, FO-EB Package was proceed the standard reliability test items includes (moisture soaking level 4, temperature cycling test 0 ɗ to 100 ɗ 3000 cycle, un-bias high accelerated stress test 264hrs and 150 ɗ high temperature storage 1000hrs). Each read point of reliability test data, O/S testing and SAT inspection were to confirm the quality result and showed all passed and summary reliability test results as shown in Table 6 Reliability and Verification Test Result.

The reliability test items total put 99 samples for Time 0 and MSL4 96 hours, then do the SAT and O/S for result verification. For TCJ, u-HUST and HTSL separate 33 samples to each of item and do the SAT with O/S to make sure the quality all well. The SAT result shows no delamination or crack with the FO-EB structure for Time Zero, MSL4, u-HAST and HTSL.

| No. | Reliability Test Items | Read Point | Sample Size | SAT & O/S Result |
| --- | --- | --- | --- | --- |
| 1 | Time Zero | TO | 0/99 pcs | All Pass |
| 2 | MSL4 (30 °C, 60% RH, 96hrs) | Pre-cond. | 0/99 pcs | All Pass |
| 3 | TCT (J) | 625, 2000,3000 | 0/33 pcs | All Pass |
|  | (0 ~ 100 °C) | Cycles |  |  |
| 4 | u-HAST (B) | 132, 264 | 0/33 pcs | All Pass |
|  | (110 °C,85%RH, 17.7 Psia) | Hours |  |  |
| 5 | HTSL (B) | 500. 1000 | 0/33 pcs | All Pass |
|  | (150 ℃. Need Pre-cond.) | Hours |  |  |

Table 6. Reliability and Verification Test Result

This paper had demonstrated the FO-EB structure with integrated Dies on the 36 mm2 ICD size. It is really difficult to overcome larger and larger TSI retical size with heterogeneous Integration, and FO-EB would be the good solution. The overall structure of Cross-section was observed in Table 7.

![](_page_5_Figure_0.png)

Table 7. Structure Cross-section Result

The SEM image of top side have side by size Dies with molded, the interface of Die to HBM shows good image and does not have crack issue. The second one shows the ICD bridge joint structure well without any non-wetting or delamniation. For the third one, the ICD molded by EMC molding compound and the interface material x-section SEM shows good adhesion result. The next one is the TIV structure shws well joint with C4 bump, and the last one is the well UF filled. The x-section image shows in Table7. Structure Crosssection Result.

## **VIII. CONCLUSION**

This paper had demonstrated the FO-EB technology included structure and feasibility data for HPC and Network application. Comparing with 2.5D and FO-MCM structure, the FO-EB not only can provide better electrical performance for HBM than FO-MCM but also the better module stress than FO-MCM. That is the reason FO-EB Package would be the best representative for HPC and Networking application. This paper had demonstrated the test vehical (TV) for FO-EB and doing the reliability test. The reliability test result shows the FO-EB Package pass the reliability test with MSL4, TCJ 3000 Cycles, u-HUST 264 Hours and HTSL1000 Hours. Completed package level reliability test for following test conditions, passed MSL4, TCJ3000, u-HAST264 and HTS1000.

### **ACKNOWLEDGMENT**

Authors would like to thank members of R&D technology development team and reliability team for their help on TV preparation and measurement setup.

### **REFERENCES**

- [1] Jeff Casazza, "First the Tick, Now the Tock: Intel Microarchitecture", in Intel White Paper, 2017, pp.1541-1546.
- [2] C. C. Lee et al., "An Overview of the Development of a GPU with Integrated HBM on Silicon Interposer", *2016 IEEE 66th Electronic Components and Technology Conference (ECTC)*, pp. 1439-1444, 2016
- [3] JEDEC Solid State Technology Association. JESD22-A104C: Temperature Cycling; 2005.
- [4] C. C. Lee et al., "An Overview of the Development of a GPU with Integrated HBM on Silicon Interposer", *2016 IEEE 66th Electronic Components and Technology Conference (ECTC)*, pp. 1439-1444, 2016
- [5] S. Y. Hou et al., "Wafer-Level Integration of an Advanced Logic-Memory System Through the Second-Generation CoWoS Technology", *IEEE Transactions on Electron Devices*, vol. 64, no. 10, pp. 4071-4077, Oct. 2017
- [6] JEDEC Solid State Technology Association, JESD22-B112A: Temperature Cycling Package Warpage Measurement of Surface-Mount Integrated Circuits at Elevated Temperature; 2009.

