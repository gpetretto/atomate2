"""
Module defining Materials Project workflows.

Reference: https://doi.org/10.1103/PhysRevMaterials.6.013801

In case of questions, consult @Andrew-S-Rosen, @esoteric-ephemera or @janosh.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from jobflow import Flow, Maker
from pymatgen.io.vasp.sets import LobsterSet

from atomate2.common.jobs.utils import remove_workflow_files
from atomate2.common.utils import _recursive_get_dir_names
from atomate2.lobster.jobs import LobsterMaker
from atomate2.vasp.flows.core import DoubleRelaxMaker
from atomate2.vasp.flows.lobster import VaspLobsterMaker
from atomate2.vasp.jobs.mp import (
    MP24PreRelaxMaker,
    MP24RelaxMaker,
    MP24StaticMaker,
    MPGGARelaxMaker,
    MPGGAStaticMaker,
    MPMetaGGARelaxMaker,
    MPMetaGGAStaticMaker,
    MPPreRelaxMaker,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from pymatgen.core.structure import Structure

    from atomate2.vasp.jobs.base import BaseVaspMaker


@dataclass
class MPGGADoubleRelaxMaker(DoubleRelaxMaker):
    """MP GGA double relaxation workflow.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker1 : .BaseVaspMaker
        Maker to generate the first relaxation.
    relax_maker2 : .BaseVaspMaker
        Maker to generate the second relaxation.
    """

    name: str = "MP GGA double relax"
    relax_maker1: Maker | None = field(default_factory=MPGGARelaxMaker)
    relax_maker2: Maker = field(
        default_factory=lambda: MPGGARelaxMaker(
            copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")}
        )
    )


@dataclass
class MPMetaGGADoubleRelaxMaker(DoubleRelaxMaker):
    """MP meta-GGA double relaxation workflow.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker1 : .BaseVaspMaker
        Maker to generate the first relaxation.
    relax_maker2 : .BaseVaspMaker
        Maker to generate the second relaxation.
    """

    name: str = "MP meta-GGA double relax"
    relax_maker1: Maker | None = field(default_factory=MPPreRelaxMaker)
    relax_maker2: Maker = field(
        default_factory=lambda: MPMetaGGARelaxMaker(
            copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")}
        )
    )


@dataclass
class MPGGADoubleRelaxStaticMaker(Maker):
    """
    Maker to perform a VASP GGA relaxation workflow with MP settings.

    Only the middle job performing a PBE relaxation is non-optional.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker : .BaseVaspMaker
        Maker to generate the relaxation.
    static_maker : .BaseVaspMaker
        Maker to generate the static calculation before the relaxation.
    """

    name: str = "MP GGA relax"
    relax_maker: Maker = field(default_factory=MPGGADoubleRelaxMaker)
    static_maker: Maker | None = field(
        default_factory=lambda: MPGGAStaticMaker(
            copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")}
        )
    )

    def make(self, structure: Structure, prev_dir: str | Path | None = None) -> Flow:
        """
        1, 2 or 3-step flow with optional pre-relax and final static jobs.

        Parameters
        ----------
        structure : .Structure
            A pymatgen structure object.
        prev_dir : str or Path or None
            A previous VASP calculation directory to copy output files from.

        Returns
        -------
        Flow
            A flow containing the MP relaxation workflow.
        """
        relax_flow = self.relax_maker.make(structure=structure, prev_dir=prev_dir)
        output = relax_flow.output
        jobs = [relax_flow]

        if self.static_maker:
            # Run a static calculation
            static_job = self.static_maker.make(
                structure=output.structure, prev_dir=output.dir_name
            )
            output = static_job.output
            jobs += [static_job]

        return Flow(jobs=jobs, output=output, name=self.name)


@dataclass
class MPMetaGGADoubleRelaxStaticMaker(MPGGADoubleRelaxMaker):
    """
    Flow with optional pre-relax and final static jobs.

    Only the middle job performing a meta-GGA relaxation is non-optional.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker : .BaseVaspMaker
        Maker to generate the relaxation.
    static_maker : .BaseVaspMaker
        Maker to generate the static calculation before the relaxation.
    """

    name: str = "MP meta-GGA relax"
    relax_maker: Maker = field(default_factory=MPMetaGGADoubleRelaxMaker)
    static_maker: Maker | None = field(
        default_factory=lambda: MPMetaGGAStaticMaker(
            copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")}
        )
    )

    def make(self, structure: Structure, prev_dir: str | Path | None = None) -> Flow:
        """Make a 2-step flow with a cheap pre-relaxation, then a high-quality one.

        An optional static calculation can be performed before the relaxation.

        Parameters
        ----------
        structure : .Structure
            A pymatgen structure object.
        prev_dir : str or Path or None
            A previous VASP calculation directory to copy output files from.

        Returns
        -------
        Flow
            A flow containing the MP relaxation workflow.
        """
        relax_flow = self.relax_maker.make(structure=structure, prev_dir=prev_dir)
        output = relax_flow.output
        jobs = [relax_flow]
        if self.static_maker:
            # Run a static calculation (typically r2SCAN)
            static_job = self.static_maker.make(
                structure=output.structure, prev_dir=output.dir_name
            )
            output = static_job.output
            jobs += [static_job]

        return Flow(jobs=jobs, output=output, name=self.name)


@dataclass
class MP24DoubleRelaxMaker(DoubleRelaxMaker):
    """MP24 PBEsol + r2SCAN double relaxation workflow.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker1 : .BaseVaspMaker
        Maker to generate the first relaxation.
    relax_maker2 : .BaseVaspMaker
        Maker to generate the second relaxation.
    """

    name: str = "MP24 double relax"
    relax_maker1: Maker | None = field(default_factory=MP24PreRelaxMaker)
    relax_maker2: Maker = field(
        default_factory=lambda: MP24RelaxMaker(
            copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")}
        )
    )


@dataclass
class MP24DoubleRelaxStaticMaker(Maker):
    """MP24 workflow to relax a structure with r2SCAN.

    Optionally, files can be automatically cleaned following completion
    of the workflow. By default, WAVECAR files are removed.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker : .BaseVaspMaker
        Maker to generate the relaxation.
    static_maker : .BaseVaspMaker
        Maker to generate the static calculation before the relaxation.
    clean_files : Sequence of str or None
        If a list of strings, names of files to remove following the workflow.
        By default, this removes the WAVECAR files (gzipped or not).
    """

    name: str = "MP24 r2SCAN workflow"
    relax_maker: Maker = field(default_factory=MP24DoubleRelaxMaker)
    static_maker: Maker = field(
        default_factory=lambda: MP24StaticMaker(
            copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")}
        )
    )
    clean_files: Sequence[str] | None = ("WAVECAR",)

    def make(self, structure: Structure, prev_dir: str | Path | None = None) -> Flow:
        """Relax a structure with r2SCAN.

        Parameters
        ----------
        structure : .Structure
            A pymatgen structure object.
        prev_dir : str or Path or None
            A previous VASP calculation directory to copy output files from.

        Returns
        -------
        Flow
            A flow containing the MP relaxation workflow.
        """
        relax_flow = self.relax_maker.make(structure=structure, prev_dir=prev_dir)

        static_job = self.static_maker.make(
            structure=relax_flow.output.structure, prev_dir=relax_flow.output.dir_name
        )

        jobs = [relax_flow, static_job]

        self.clean_files = self.clean_files or []
        if len(self.clean_files) > 0:
            directories: list[str] = []
            _recursive_get_dir_names(jobs, directories)
            cleanup = remove_workflow_files(
                directories=directories,
                file_names=self.clean_files,
                allow_zpath=True,
            )
            jobs += [cleanup]

        return Flow(jobs=jobs, output=static_job.output, name=self.name)


# update potcars to 54, use correct W potcar
# use staticmaker for compatibility
@dataclass
class MPVaspLobsterMaker(VaspLobsterMaker):
    """
    Maker to perform a Lobster computation.

    The calculations performed are:

    1. Optional optimization.
    2. Static calculation with ISYM=0.
    3. Several Lobster computations testing several basis sets are performed.

    .. Note::

        The basis sets can only be changed with yaml files.

    Parameters
    ----------
    name : str
        Name of the flows produced by this maker.
    relax_maker : .BaseVaspMaker or None
        A maker to perform a relaxation on the bulk. Set to ``None`` to skip the
        bulk relaxation.
    lobster_static_maker : .BaseVaspMaker
        A maker to perform the computation of the wavefunction before the static
        run. Cannot be skipped. It can be LOBSTERUNIFORM or LobsterStaticMaker()
    lobster_maker : .LobsterMaker
        A maker to perform the Lobster run.
    delete_wavecars : bool
        If true, all WAVECARs will be deleted after the run.
    address_min_basis : str
        A path to a yaml file including basis set information.
    address_max_basis : str
       A path to a yaml file including basis set information.
    """

    name: str = "lobster"
    relax_maker: BaseVaspMaker | None = field(default_factory=MPGGADoubleRelaxMaker)
    lobster_static_maker: BaseVaspMaker = field(
        default_factory=lambda: MPGGAStaticMaker(input_set_generator=LobsterSet())
    )
    lobster_maker: LobsterMaker | None = field(default_factory=LobsterMaker)
    delete_wavecars: bool = True
    address_min_basis: str | None = None
    address_max_basis: str | None = None
