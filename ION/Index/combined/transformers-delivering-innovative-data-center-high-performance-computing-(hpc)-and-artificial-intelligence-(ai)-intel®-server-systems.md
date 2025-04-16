# Transformers: Delivering Innovative Data Center High performance computing (HPC) and Artificial Intelligence (AI) Intel® Server Systems

Anupama Balasubramanian, *Intel Corporation,* anupama.balasubramanian@Intel.com; Drew Damm, *Intel Corporation,* drew.g.damm@Intel.com; Sam Melhem, *Intel Corporation*, sam.m.melhem@intel.com ; Andrew C Dausman, *Intel Corporation,* andrew.c.dausman@intel.com; Joshua T Linden Levy, *Intel Corporation*, joshua.t.linden.levy@intel.com; Yingqiong Bu, *Intel Corporation*, yingqiong.bu@intel.com ; Brian Mao, *Intel Corporation, brian.mao@intel.com* ; Craig S Cauvel, *Intel Corporation*, Craig.s.cauvel@intel.com

*Abstract*—*In an environment where the most power and performance is needed at the least cost, engineering is always looking at how to optimize existing hardware features. This is done through system engineering solutions and optimized software. This paper will describe the concept architecture, design and development cycle of how a High performance computing (HPC) and Artificial Intelligence (AI) Intel® Server System product family featuring Intel® Xeon® Platinum processors was manufactured. This was a grounds-up server chassis design with one chassis supporting multiple skus with air and liquid cooling, half and full width, & 1U/2U options all in one highly configurable system. The paper will cover the unique features including front I/O and shared cooling to start. The next section dives into the modeling techniques used that allowed to compress the manufacturing cycle to permit going from prototype to Hard Tool Chassis within 20 weeks. Using HT samples for the entire product qualification enabled the team to shift left and build confidence on product quality and reliability. We then deep dive and conclude with the Outsource Design Manufacturer (ODM) engagement and the technical challenges encountered in delivering this chassis backed by Intel's design excellence and manufacturing expertise with processing power enabling high levels of flexibility, manageability, and reliability.*

*Keywords—Intel, Chassis, HPC, Manufacturing, Configurable, Server* 

# I. INTRODUCTION

While chassis are vital for all server systems they are at the bottom of the product sku stack as they are considered relatively easy to manufacture and not as complicated as processor design. The profit margins are also very low and the competition is high. There is very little published information available to provide detail on this and most is tribal knowledge as chassis are typically sold as part of a whole system or invisible to the end user. Plus technological advances from generation to generation in server processors sometimes does not allow us to reuse an existing L3 frame. This leads to repeated design and development cycles leading to increased cost and lack of efficiency from a product time to market cycle. As a result the need to provide a robust and flexible infrastructure that supports multiple generations of

future products for a large variety of compute and storage options is significant.

FC2000 chassis is intended to be a flexible infrastructure that is not tied to any specific CPU platform. The system defines a set of physical form factors and provides common interfaces for power and management. The system also provides options for high performance air cooling and liquid cooling. The air cooled option is intended to be best-in-class. The liquid cooling option enables high compute density at maximum TDP and supports liquid heat capture to help to minimize TCO (Total Cost of Ownership).

This paper will describe the concept architecture, design and development cycle of how this FC2000 chassis was manufactured and brought to market.

### II. CHASSIS FEATURES

![](_page_0_Picture_10.png)

Figure 1: FC2000 L3 Chassis overview

The FC2000 chassis has a number of unique features that were architected in to meet the needs of Intel and our customers that are different from previous chassis generations currently available in the High Performance Computing market. First is the high-density of compute that it provides to our customers where floor and rack space is limited. The FC200 can support the newest and highest performing CPUs in Intel's Data Center range such as the Intel® Xeon® Platinum 9200 processors. It features highairflow capability in order to extend the technology lifetime of air cooling for our customers that are not configured for liquid cooling while still cooling top-of-the-line CPUs. It also provides the ability for liquid cooling to support our customers that are looking to recover as much heat capture in their datacenter as possible.

The FC2000 chassis architecture is designed to provide maximum configuration flexibility to Intel's customers and provide a common set of mechanical components for the manufacturing process. This reduces overall cost of assembling and sustaining the chassis as multiple chassis configurations can be built from the same set of building blocks. The FC2000 chassis can be configured in any permutation of 1U or 2U sled heights, half-width or fullwidth sled heights, and liquid cooling or air cooling. This permits eight distinct chassis configurations and also permits the potential to support specific heterogeneous sled configuration options. Many of these sled options have been announced and are available in the market today. Some sled configurations are in product development. Best of all, some sled configurations have not yet been developed, but are already supported by the FC2000 chassis architecture.

![](_page_1_Figure_2.png)

Figure 2: FC2000 Chassis System top and side view

#### A. *Sled Features*

The FC2000's sled permutation is determined "just in time" when the L3 chassis sheet metal is assembled. This reduces planning expense from stocking chassis configurations that are not needed for currently selling products and prevents maintaining an expensive inventory of different chassis. To configure the chassis for half-width sleds, a single additional wall is permanently assembled in to the chassis. The support for 1U or 2U height sleds is provided by a set of support brackets that are able to be installed or removed with a simple tool and can be adjusted either by Intel field service, or the end customers themselves.

![](_page_1_Figure_6.png)

Figure 3: Expanded/Staggered view of the chassis showing the various brackets for sled configurations

There are 6 sleds with different form factors developed that can fit into the FC2000 chassis, and can consist of compute, storage, I/O, accelerators etc., in any combination that can fit within the physical, thermal, and power constraints. Sleds can support low profile PCIe card, 22 x 80 or 22 x 110 mm M.2 card, U.2 drive, EDSFF E1.L NVMe SSDs, full width full height PCIe card in specific sleds.

![](_page_1_Figure_9.png)

Figure 4: 1U Half Width Air cooling Sled

![](_page_2_Picture_0.png)

Figure 5: 2U Half Width Air cooling Sled

![](_page_2_Picture_2.png)

Figure 6: 2U Half Width Storage Sled

![](_page_2_Picture_4.png)

Figure 7: 1U Half Width Liquid Cooling Sled

![](_page_2_Picture_6.png)

Figure 8: 2U Half Width Liquid cooling Sled

![](_page_2_Picture_8.png)

Figure 9: 2U Full Width Air Cooling Sled

#### B. *Cooling Features*

Cooling technology in the FC2000 is also determined "just in time", but at the L5 level. For air-cooling, 80mm fans Customer Replaceable Units (CRUs) are installed into the outside fan bays. When configuring a liquid-cooled chassis, the chassis-side liquid manifold loop is installed down into the system and the liquid quick disconnects exit the chassis in the same outside bays as the 80mm fans in an air-cooled configuration. The liquid quick disconnects are physically supported by sheet metal brackets that use the same locating and latching features as the 80mm fans. A key difference is that the liquid quick disconnect support brackets have a latch feature that require a simple tool to remove to prevent accidental removal by a customer. Finally, common 60mm fans are installed along with the power supplies regardless of whether the system is being configured for air or liquidcooling at the L5 level. For future platforms that may need additional air flow requirements (in liquid-cooling configuration), the chassis was configured to allow additional 60mm Fan CRUs to be installed in available bay openings above the liquid disconnect support brackets.

![](_page_3_Figure_0.png)

Figure 10: View of the chassis showing the various cooling options for air and liquid and the fans

![](_page_3_Figure_2.png)

![](_page_3_Figure_3.png)

Figure 12: Liquid cooled back view component description

To meet the need for adaptability to install the FC2000 chassis into a non-specified Rack configuration, multipositional Rack Ears (with handle) were designed that will allow the customer to adjust the front-to-back position to configure chassis location relative to the Rack's front vertical support member. Additionally, Rear Chassis Support Brackets are provided for in-Rack shipping.

#### III. CHASSIS MODELING

"Skeleton" modeling techniques were used during the design process in order to simultaneously control the related dimensions of a large number of mechanical parts. This is a "top-down" computer aided design method and is different than relying on driving in-context relationships between parts and assemblies in a parametric CAD environment. The design team used the skeleton geometry and publish geometry features of Parametric Technologies (PTC) Creo Parametric to ensure that volume and location constraints were satisfied throughout the entire system. In many of the key L1 piece parts, the designer would begin by importing the skeleton model as a "published geometry" feature into the model tree. This gave the designer the context of the entire system, without having to work inside of the graphically intensive top-level CAD models.

For example, several of the part models that form the exterior of the chassis structure had their width and heights controlled by relating the sketches to the master model skeleton geometry. These parts had their extrude depth controlled by extruding the solid features up to planes that were also located inside the skeleton model.

This technique paid off during the development phase when the team decided to change the overall chassis height and width from what was originally planned. The external chassis dimensions were updated to the new size in the skeleton model which was checked into the version control system. The next time a designer on the team updated his or her CAD environment, the new skeleton would automatically update all impacted parts. Even if the designer was only working on a single piece part, the skeleton model would drive changes to the new dimensions. This saved time because changes only needed to be made a single time at the skeleton. It also prevented any mistakes due to miscommunication between design engineers located in various geos and working simultaneously.

#### IV. DESIGN CHALLEGNES

Maintaining static and dynamic structural integrity is one of the largest challenges the design team worked to overcome during development in order to ensure the system was sufficiently robust to withstand shocks and vibration in a cost effective shipping package. This system was particularly structurally challenging due to the high and concentrated loads it needed to support. Many structural features were added to the chassis design intended to meet the static and dynamic sag requirements

Extensive Finite Element Analysis (FEA) was performed throughout the design process and correlated with empirical shock and vibration testing. The FEA was used to drive decision making about the swage pitch and dimensions of the structural sub-floor, where the chassis would benefit the most from increased structure and structural component wall thickness.

System "sag" was a major design driver for this system due to the large loads. However, system sag is a multi-faceted problem. Engineers must account for the inherent shape of the chassis due to manufacturing processes (including tolerance variation), the change in shape to the self-weight of the sheet metal, and the incremental sag of the chassis due to loading it with nodes. All chassis will have some incoming shape due to manufacturing (either sagging in the negative z direction or bowing in the positive z direction). It is not possible to predict inherent shape due to manufacturing variation through simulation, this must be controlled through testing and manufacturing specifications.

One of the earliest learnings, from pre-power on system testing, was that the structural mid-wall needed to be improved to survive the dynamic shocks associated with shipping a Rack-Scale deployment without the chassis violating the U-space requirement. The material was changed in order to prevent plastic deformation of the structural member. As shall be discussed in the following section, although ultimately successful, this design choice resulted in myriad manufacturing challenges.

#### V. MANUFACTURING CHALLENGES

The team used a TRIAD consisting of the Manufacturing Development Engineer, Materials Engineer and the Design Engineer to follow a consistent method for conducting piece part qualifications of the chassis parts used in systems, accessories, spares, subassemblies, rail assemblies, and all productized items that will be part of the platform launch.

The evaluation is inclusive of all sheet metal and plastic parts and is a gate to part promotion for production. This process was used to evaluate hard tool parts, & associated tooling, that was used in production. If a soft tooled part will be used in production, then the Triad would review any available dimensional soft tooled data, understanding that Process Capability Index (Cpk) data is not relevant to soft tooled parts. For soft tooled parts used for product development during NPI, the same Triad reviews occur as for hard tools, minus the Cpk data.

#### A. *Mid-Wall Tooling Challenges*

Due to some miscommunication and varying standards achieving the correct dimensions on the mid-wall, the manufacturing of selected material and thickness proved quite difficult. The exact properties that made the material desirable for structural (namely high yield strength) made it more difficult to form in standard, multi-cavity, sheet-metal tooling. This resulted in a lot of Design for Manufacturing (DFM) design change requests from the vendor that were difficult from various thermal, structural and design aspects.

The first impact evaluated was in the thermal domain, the vendor request for an increase in webbing thickness for the new material caused a measureable increase in impedance to system airflow. The second DFM impact was that the locations of some major interface components in the design needed to be changed. Finally, the team actually saw an increase in structural performance (due to the same DFM feedback).

In order to deal with the DFM feedback we took a threefold approach to structural simulation, at a component level, to evaluate the impact to the system. First we looked at the incoming sag level. Due to empirical testing we started by placing the incoming shape of the chassis at our max allowable sag defined for the inseparable sheet metal assemble (ISA). We bumped this up for conservatism. To this was then added the impact of elastic sag. Finally, the impact of plastic sag was included. The sum total of these analyses showed that the manufacturing changes would in fact provide a more robust mid-wall geometry.

#### B. *Material Standards Ambiguity*

Furthermore, there is some ambiguity between ASTM and JIS standards around material temper and the property values those entail. The design team learned that the best way to specify the material was to only list the properties that were Critical to Function (CTF). In fact, specifying details beyond that (JIS vs ASTM, Temper, Modulus) served only to obfuscate the issue and confuse both the design team and our manufacturing partners.

#### C. *Third Party Material Testing*

Due to the massive communication issues in defining the structural material, the team decided it was necessary to use a third party testing lab to certify the mother coil material Production Part Approval. Third party labs must be certified to perform testing covered by ASTM.

Sample preparation, specifically, per ASTM E8/E8M, Section 6 "Test Specimens" seems an area for particular attention. "*Improperly prepared test specimens often are the reason for unsatisfactory and incorrect test results. It is important, therefore, that care be exercised in the preparation of specimens, particularly in the machining, to maximize precision and minimize bias in test results*."

Another concern is the orientation with which the sample is removed from the mother material. The grain direction is in the rolling direction of the sheet as it was being manufactured. Although tempering, by reheating the material above the re-crystallization temperature, allows the crystal grains to become more uniform; there is residual anisotropy in the material. Samples at at least 90 degree orientations should be inspected (if not 45 degrees).

#### VI. DEVELOPMENT AND EXECUTION

It was decided from the beginning to use Hard Tooled chassis very early in the Product life cycle due to reduced cost and also allowing internal validation teams to run tests on the actual product. We went from prototypes to hard tool chassis in 20 weeks. Once TRIAD team completed qualification of soft tooled chassis (parts, L3, L5, and L9) and completion of dynamic testing, it was a straight forward step to go into hard tooling phase. This was hugely accelerated by on site presence of the team at the ODM during soft and hard tooling phases. A total of 100+ piece part and subassemblies have been approved after so many mechanical evaluations, qualifications, and design updates.

This chassis is part of an L9 system delivered to our customers, and de-risking the chassis ahead of schedule was critical for the program's success. There was significant cost reduction also because HT chassis are ~4X cheaper than ST chassis. Using HT samples for the entire product qualification enabled the team to shift left and build confidence on product quality and reliability performance 1.5Q before product release. This is one of the first times any Intel program has had a HT chassis for early validation meeting Intel's stringent product requirements.

For this program, the design team also deployed a new system of external, Product Data Management (PDM) tools in order to work more closely with our external design partners. We leveraged internal and PTC resources in order to allow our external design partners access to our MCAD database. This dramatically decreased security risks found in traditional data exchange, as well as increasing the speed of execution, and collaboration efficiency between our suppliers, partners and internal engineers resulting in hundreds of thousands of dollars of cost savings and millions of dollars of cost avoidance.

## VII. CONCLUSION

This paper describes in detail the whole design, development and manufacturing cycle of the FC200 Intel HPC Chassis system that enabled samples to be available for Intel's marketing demo at the 2018 super computing show and de-risked the chassis ahead of the program schedule by more than a quarter. The team continues to look at further opportunities to optimize the chassis design for better performance, easier manufacturing and reduced cost to continue to delight our customers.

#### ACKNOWLEDGMENT

The team would like to acknowledge the following individuals for their work during the various phases of development of this chassis. Gene Young and Andrew Thompson were the architects who passionately believed this chassis could be engineered. Brian Caslis never took no from engineering and always was the voice of the customer. Guocheng Zhang drove a lot of the design support and fixed bugs and issues, Dana Grindle drove integration during the later stages of the program, Carl Williams provided design support during the early development stages, John Carver was the 80mm fan lead design engineer, Ameya Limaye owned a lot of the structural assessments for early designs, Jorge Chagoya Bello and Carlos Terriquez Arias provided design support. Don Hammon, Alex Zhang, Craig Zhang and Xiang Xiao drove ensuring that our manufacturing partner delivered the chassis meeting Intel's specifications. Jose Camargo Rojas and Si Guang Qin ensured that the materials we chose and the pricing provided from vendors was competitive and met Intel design and qualification specifications.

