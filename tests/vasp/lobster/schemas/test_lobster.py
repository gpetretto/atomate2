def test_LobsterTaskDocument(lobster_test_dir):
    """
    Test the CCDDocument schema, this test needs to be placed here
    since we are using the VASP TaskDocuments for testing.
    """

    import numpy as np
    from pymatgen.core.structure import Structure
    from pymatgen.electronic_structure.cohp import Cohp, CompleteCohp
    from pymatgen.electronic_structure.dos import LobsterCompleteDos

    from atomate2.lobster.schemas import (
        LobsterinModel,
        LobsteroutModel,
        LobsterTaskDocument,
        StrongestBonds,
    )

    doc = LobsterTaskDocument.from_directory(
        dir_name=lobster_test_dir / "lobsteroutputs/mp-2534",
        save_cohp_plots=False,
        calc_quality_kwargs={"n_bins": 100, "potcar_symbols": ["Ga_d", "As"]},
        save_cba_jsons=False,
        save_computational_data_jsons=False,
    )
    assert isinstance(doc.structure, Structure)
    assert isinstance(doc.lobsterout, LobsteroutModel)
    assert np.isclose(doc.lobsterout.charge_spilling[0], 0.009899999999999999)

    assert isinstance(doc.lobsterin, LobsterinModel)
    assert np.isclose(doc.lobsterin.cohpstartenergy, -5)
    assert isinstance(doc.strongest_bonds_icohp, StrongestBonds)
    assert np.isclose(
        doc.strongest_bonds_icohp.strongest_bonds["As-Ga"]["ICOHP"], -4.32971
    )
    assert np.isclose(
        doc.strongest_bonds_icobi.strongest_bonds["As-Ga"]["ICOBI"], 0.82707
    )
    assert np.isclose(
        doc.strongest_bonds_icoop.strongest_bonds["As-Ga"]["ICOOP"], 0.31405
    )
    assert np.isclose(
        doc.strongest_bonds_icohp.strongest_bonds["As-Ga"]["length"], 2.4899
    )
    assert np.isclose(
        doc.strongest_bonds_icobi.strongest_bonds["As-Ga"]["length"], 2.4899
    )
    assert np.isclose(
        doc.strongest_bonds_icoop.strongest_bonds["As-Ga"]["length"], 2.4899
    )
    assert doc.strongest_bonds_icoop.which_bonds == "all"
    assert doc.strongest_bonds_icohp.which_bonds == "all"
    assert doc.strongest_bonds_icobi.which_bonds == "all"
    assert np.isclose(
        doc.strongest_bonds_icohp_cation_anion.strongest_bonds["As-Ga"]["ICOHP"],
        -4.32971,
    )
    assert np.isclose(
        doc.strongest_bonds_icobi_cation_anion.strongest_bonds["As-Ga"]["ICOBI"],
        0.82707,
    )
    assert np.isclose(
        doc.strongest_bonds_icoop_cation_anion.strongest_bonds["As-Ga"]["ICOOP"],
        0.31405,
    )
    assert np.isclose(
        doc.strongest_bonds_icohp_cation_anion.strongest_bonds["As-Ga"]["length"],
        2.4899,
    )
    assert np.isclose(
        doc.strongest_bonds_icobi_cation_anion.strongest_bonds["As-Ga"]["length"],
        2.4899,
    )
    assert np.isclose(
        doc.strongest_bonds_icoop_cation_anion.strongest_bonds["As-Ga"]["length"],
        2.4899,
    )
    assert doc.strongest_bonds_icoop_cation_anion.which_bonds == "cation-anion"
    assert doc.strongest_bonds_icohp_cation_anion.which_bonds == "cation-anion"
    assert doc.strongest_bonds_icobi_cation_anion.which_bonds == "cation-anion"
    assert isinstance(doc.lobsterpy_data.cohp_plot_data["Ga1: 4 x As-Ga"], Cohp)
    assert doc.lobsterpy_data.which_bonds == "all"
    assert doc.lobsterpy_data_cation_anion.which_bonds == "cation-anion"
    assert doc.lobsterpy_data.number_of_considered_ions == 2
    assert isinstance(
        doc.lobsterpy_data_cation_anion.cohp_plot_data["Ga1: 4 x As-Ga"], Cohp
    )
    assert isinstance(doc.lobsterpy_text, str)
    assert isinstance(doc.lobsterpy_text_cation_anion, str)

    assert isinstance(doc.cohp_data, CompleteCohp)
    assert isinstance(doc.cobi_data, CompleteCohp)
    assert isinstance(doc.coop_data, CompleteCohp)
    assert isinstance(doc.dos, LobsterCompleteDos)
    assert np.isclose(doc.madelung_energies["Mulliken"], -0.68)
    assert np.allclose(
        doc.site_potentials["Mulliken"],
        [-1.26, -1.27, -1.26, -1.27, 1.27, 1.27, 1.26, 1.26],
        rtol=1e-2,
    )
    assert np.isclose(doc.site_potentials["Ewald_splitting"], 3.14)
    assert len(doc.gross_populations) == 8
    assert doc.gross_populations[5]["element"] == "As"
    expected_gross_popp = {
        "4s": 1.38,
        "4p_y": 1.18,
        "4p_z": 1.18,
        "4p_x": 1.18,
        "total": 4.93,
    }
    gross_popp_here = doc.gross_populations[5]["Loewdin GP"]
    assert expected_gross_popp == gross_popp_here
    assert np.allclose(
        doc.charges["Mulliken"],
        [0.13, 0.13, 0.13, 0.13, -0.13, -0.13, -0.13, -0.13],
        rtol=1e-2,
    )
    assert len(doc.band_overlaps["1"]) + len(doc.band_overlaps["-1"]) == 12

    assert doc.chemsys == "As-Ga"

    doc2 = LobsterTaskDocument.from_directory(
        dir_name=lobster_test_dir / "lobsteroutputs/mp-754354",
        save_cohp_plots=False,
        calc_quality_kwargs={"n_bins": 100, "potcar_symbols": ["Ba_sv", "O", "F"]},
        save_cba_jsons=False,
        save_computational_data_jsons=False,
    )
    assert np.isclose(
        doc2.strongest_bonds_icohp.strongest_bonds["Ba-O"]["ICOHP"], -0.55689
    )
    assert np.isclose(
        doc2.strongest_bonds_icohp.strongest_bonds["Ba-F"]["ICOHP"], -0.44806
    )
    assert len(doc2.band_overlaps["1"]) + len(doc2.band_overlaps["-1"]) == 2
    assert np.allclose(
        doc2.site_potentials["Loewdin"],
        [
            -15.09,
            -15.09,
            -15.09,
            -15.09,
            -15.09,
            -15.09,
            -15.09,
            -15.09,
            14.78,
            14.78,
            8.14,
            8.14,
            8.48,
            8.48,
            8.14,
            8.14,
            8.14,
            8.14,
            8.48,
            8.48,
            8.14,
            8.14,
        ],
        rtol=1e-2,
    )
    assert np.isclose(doc2.site_potentials["Ewald_splitting"], 3.14)
    assert len(doc2.gross_populations) == 22
    assert doc2.gross_populations[10]["element"] == "F"
    expected_gross_popp = {
        "2s": 1.98,
        "2p_y": 1.97,
        "2p_z": 1.97,
        "2p_x": 1.97,
        "total": 7.88,
    }
    gross_popp_here = doc2.gross_populations[10]["Mulliken GP"]
    assert expected_gross_popp == gross_popp_here


def test_lobstertaskdocument_saved_jsons(lobster_test_dir):
    """
    Test if jsons are saved are valid
    """
    import os

    from pymatgen.electronic_structure.cohp import Cohp, CompleteCohp
    from pymatgen.electronic_structure.dos import LobsterCompleteDos

    from atomate2.lobster.schemas import (
        LobsterTaskDocument,
        read_saved_json,
    )

    # Generate condensed bonding analysis (cba) json using lobstertaskdoc

    _ = LobsterTaskDocument.from_directory(
        dir_name=lobster_test_dir / "lobsteroutputs/mp-2534",
        save_cohp_plots=False,
        calc_quality_kwargs={"n_bins": 100, "potcar_symbols": ["Ga_d", "As"]},
        save_cba_jsons=True,
        add_coxxcar_to_task_document=False,
        save_computational_data_jsons=False,
    )

    expected_cba_keys_json = [
        "cation_anion_bonds",
        "all_bonds",
        "madelung_energies",
        "charges",
        "calc_quality_summary",
        "calc_quality_text",
        "dos",
        "lso_dos",
        "builder_meta",
    ]

    for cba_key in expected_cba_keys_json:
        # read data from saved json as pymatgen objects
        json_data = read_saved_json(
            filename=lobster_test_dir / "lobsteroutputs/mp-2534/cba.json.gz",
            pymatgen_objs=True,
            query=cba_key,
        )

        if "dos" in cba_key and json_data[cba_key]:
            assert isinstance(json_data[cba_key], LobsterCompleteDos)

        if (cba_key == "all_bonds" or cba_key == "cation_anion_bonds") and json_data[
            cba_key
        ]:
            for cohp_data in json_data[cba_key]["lobsterpy_data"][
                "cohp_plot_data"
            ].values():
                assert isinstance(cohp_data, Cohp)

    # read cba saved jsons without converting it to non pymatgen objects (read as dict)

    for cba_key in expected_cba_keys_json:
        json_data = read_saved_json(
            filename=lobster_test_dir / "lobsteroutputs/mp-2534/cba.json.gz",
            pymatgen_objs=False,
            query=cba_key,
        )
        if "dos" in cba_key and json_data[cba_key]:
            assert isinstance(json_data[cba_key], dict)

        if (cba_key == "all_bonds" or cba_key == "cation_anion_bonds") and json_data[
            cba_key
        ]:
            for cohp_data in json_data[cba_key]["lobsterpy_data"][
                "cohp_plot_data"
            ].values():
                assert isinstance(cohp_data, dict)

    # delete the cba json after the test
    os.remove(lobster_test_dir / "lobsteroutputs/mp-2534/cba.json.gz")

    # Generate computational data json from lobstertaskdoc
    _ = LobsterTaskDocument.from_directory(
        dir_name=lobster_test_dir / "lobsteroutputs/mp-754354",
        save_cohp_plots=False,
        calc_quality_kwargs={"n_bins": 100, "potcar_symbols": ["Ba_sv", "O", "F"]},
        save_cba_jsons=False,
        add_coxxcar_to_task_document=False,
        save_computational_data_jsons=True,
    )

    expected_computational_data_keys_json = [
        "builder_meta",
        "structure",
        "charges",
        "lobsterout",
        "lobsterin",
        "lobsterpy_data",
        "lobsterpy_text",
        "calc_quality_summary",
        "calc_quality_text",
        "strongest_bonds_icohp",
        "strongest_bonds_icoop",
        "strongest_bonds_icobi",
        "lobsterpy_data_cation_anion",
        "lobsterpy_text_cation_anion",
        "strongest_bonds_icohp_cation_anion",
        "strongest_bonds_icoop_cation_anion",
        "strongest_bonds_icobi_cation_anion",
        "dos",
        "lso_dos",
        "madelung_energies",
        "site_potentials",
        "gross_populations",
        "band_overlaps",
        "cohp_data",
        "coop_data",
        "cobi_data",
    ]

    # Read the data from saved computational data json as pymatgen objects
    for taskdoc_key in expected_computational_data_keys_json:
        json_data = read_saved_json(
            filename=lobster_test_dir
            / "lobsteroutputs/mp-754354/computational_data.json.gz",
            pymatgen_objs=True,
            query=taskdoc_key,
        )
        if "dos" in taskdoc_key and json_data[taskdoc_key]:
            assert isinstance(json_data[taskdoc_key], LobsterCompleteDos)

        if "lobsterpy_data" in taskdoc_key and json_data[taskdoc_key]:
            for cohp_data in json_data[taskdoc_key]["cohp_plot_data"].values():
                assert isinstance(cohp_data, Cohp)

        if (
            taskdoc_key == "cohp_data"
            or taskdoc_key == "cobi_data"
            or taskdoc_key == "coop_data"
        ) and json_data[taskdoc_key]:
            assert isinstance(json_data[taskdoc_key], CompleteCohp)

    # delete the computational data json after the test
    os.remove(lobster_test_dir / "lobsteroutputs/mp-754354/computational_data.json.gz")
