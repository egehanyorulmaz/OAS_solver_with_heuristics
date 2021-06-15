# Heuristics for order acceptance and scheduling problem

Due to the limited production capacity of the make-to-order production system, the acceptance of an order and the scheduling decision are made at the same time when delivery requirements are made and orders must be selected to maximize total return. Taking into account the impact on production capacity, accepting orders may result in overloads in some periods, which causes some orders to be overdue and delayed. 

# Problem description

A manufacturer receives n orders from its customers. A set of independent orders (tasks) O is assigned to be processed on a single machine at the start of the planning period. Each order  requires a certain amount of release time ri, processing time pi, due date di, deadline , revenue ei denoting the maximum gain from order i, and unit tardiness penalty cost wi. The manufacturer's capacity is not enough to process all orders on time, so it is necessary to decide a set of accepted orders. It is assumed that the manufacturer has only one workstation and can process a maximum of one order at a time. Since each order has a due date; if the order is completed beyond its due date, a penalty will be incurred. Therefore, the processing sequence for accepting orders must also be determined. The goal is to maximize total revenue after subtracting penalty costs. 
