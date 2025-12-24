# -*- coding: utf-8 -*-
from pyrevit import revit, DB, script

output = script.get_output()

def get_parameter_value(element, param_name):
    param = element.LookupParameter(param_name)
    if param:
        if param.StorageType == DB.StorageType.String:
            return param.AsString()
        elif param.StorageType == DB.StorageType.Double:
            return param.AsDouble()
        elif param.StorageType == DB.StorageType.Integer:
            return param.AsInteger()
        elif param.StorageType == DB.StorageType.ElementId:
            return param.AsElementId().IntegerValue
    return None

def main():
    doc = revit.doc
    collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_ElectricalEquipment).WhereElementIsNotElementType()
    
    equipments = collector.ToElements()
    
    if not equipments:
        output.print_md("## No Electrical Equipments found in the project.")
        return

    output.print_md("## Electrical Equipments QC Data")
    
    for eq in equipments:
        output.print_md("---")
        output.print_md("### ID: {}".format(eq.Id))
        output.print_md("**Name:** {}".format(eq.Name))
        
        # Get all parameters
        params = eq.Parameters
        if params:
            data = []
            for p in params:
                val = ""
                if p.StorageType == DB.StorageType.String:
                    val = p.AsString()
                elif p.StorageType == DB.StorageType.Double:
                    # Format double if needed, raw for now
                    val = str(p.AsDouble())
                elif p.StorageType == DB.StorageType.Integer:
                    val = str(p.AsInteger())
                elif p.StorageType == DB.StorageType.ElementId:
                    val = str(p.AsElementId().IntegerValue)
                
                if val is None:
                    val = "None"
                    
                data.append([p.Definition.Name, val])
            
            # Sort by parameter name
            data.sort(key=lambda x: x[0])
            
            # Print as table
            output.print_table(table_data=data, columns=["Parameter", "Value"])

if __name__ == "__main__":
    main()
