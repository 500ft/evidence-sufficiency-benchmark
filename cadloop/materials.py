"""SOLIDWORKS material identity and document-level mass-property readback."""
import pythoncom
import win32com.client
import os
from pathlib import Path

DEFAULT_DATABASE=Path(os.environ.get('CADLOOP_MATERIAL_DATABASE',r'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS (2)\lang\english\sldmaterials\solidworks materials.sldmat'))
ALUMINUM_6061_T6='6061-T6 (SS)'


def member(obj,name):
    value=getattr(obj,name)
    return value() if callable(value) and not hasattr(value,'_oleobj_') else value


def read_part_material(part):
    database=win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_BSTR,'')
    name=part.GetMaterialPropertyName2('',database)
    properties=member(part.Extension,'CreateMassProperty')
    properties.UseSystemUnits=True
    return {'material_name':name,'material_database':database.value,
            'density_kg_m3':float(properties.Density),'mass_kg':float(properties.Mass),
            'volume_m3':float(properties.Volume),
            'center_of_mass_m':list(properties.CenterOfMass),
            'override_mass':bool(properties.OverrideMass),
            'override_center_of_mass':bool(properties.OverrideCenterOfMass),
            'override_moments':bool(properties.OverrideMomentsOfInertia)}


def assign_part_material(part,database,name):
    # This method returns void. Readback, rather than its return value, proves assignment.
    part.SetMaterialPropertyName2('',str(database),name)
    part.ForceRebuild3(False)
    actual=read_part_material(part)
    if actual['material_name']!=name:raise RuntimeError('Material assignment did not persist')
    return actual
