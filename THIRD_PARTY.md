
# Third-party Attribution

This public release demonstrates engineering around PET/CT AI reproducibility. It does not claim ownership of upstream model architectures, challenge assets, preprocessing code, or framework code.

| Project | Role | Status |
| --- | --- | --- |
| AutoPET | Challenge/task context and dataset ecosystem. | Third-party; not copied here. |
| nnU-Net | Upstream segmentation framework invoked by optional wrappers. | Third-party; architecture and framework remain upstream work. |
| LesionTracer / Team LesionTracer | FDG20 fixed-prediction model family and upstream AutoPET III implementation. | [Official implementation](https://github.com/MIC-DKFZ/autopet-3-submission); upstream code repository carries Apache-2.0. Its [final checkpoint distribution](https://zenodo.org/records/14007247) is separate. No model weights are included or redistributed here; this attribution does not establish the byte identity or reuse terms of protected local checkpoint copies. |
| Blackbean | Historical local project dependency/context. | HISTORICAL_PROJECT_RECORD where mentioned; not copied here. |
| TCIA_processing | Historical local preprocessing context. | HISTORICAL_PROJECT_RECORD where mentioned; not copied here. |

No upstream repositories, model weights, challenge code, or patient data are included in this release. The upstream code license is not a blanket license for separately distributed weights; consult the upstream checkpoint record for its terms before use or redistribution.
