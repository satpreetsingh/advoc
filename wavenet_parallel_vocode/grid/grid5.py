import os

TRAIN_TEMPL = """
export CUDA_VISIBLE_DEVICES="{gpunum}"
TRAIN_DIR={traindir}
rm -rf ${{TRAIN_DIR}}
mkdir ${{TRAIN_DIR}}
git rev-parse HEAD > ${{TRAIN_DIR}}/git_sha.txt
python train_evaluate.py train ${{TRAIN_DIR}} \\
    --data_dir {datadir}/train \\
    --model wavenet_vocoder \\
    --model_overrides "{model_overrides}"
"""

EVAL_TEMPL = """
export CUDA_VISIBLE_DEVICES="-1"
TRAIN_DIR={traindir}
python train_evaluate.py eval ${{TRAIN_DIR}} \\
    --data_dir {datadir}/valid \\
    --model wavenet_vocoder \\
    --model_overrides "{model_overrides}"
"""

DATE_STR = "03_19"
EXP_OFFSET = 0
TRAINDIR_ROOT = '/storage/models'
DATADIR = '/storage/data/LJSpeech-1.1/wavs_split'

EXP_ALL_HYPER = [
    ('input_type', 'gaussian_spec'),
    ('input_spec_upsample', 'default'),
    ('train_recon_domain', 'r9y9'),
    ('train_recon_multiplier', '1'),
    ('train_batch_size', '30'),
    ('train_lr', '0.0001'),
    ('train_distill_ckpt_fp', '/storage/code/advoc/advoc/wavenet_parallel_vocode/eval/wavenet_auto_small/best-88141'),
    ('eval_wavenet_metagraph_fp', '/storage/code/advoc/advoc/wavenet_parallel_vocode/eval/wavenet_auto_small/infer.meta'),
    ('eval_wavenet_ckpt_fp', '/storage/code/advoc/advoc/wavenet_parallel_vocode/eval/wavenet_auto_small/best-88141'),
]

EXPS = [
    ("gausspec_distill_wavenet", [
      ('train_distill', 'True'),
      ('train_distill_multiplier', '0.01'),
    ]),
    ("gausspec_if_l2", [
      ('train_if', 'True'),
      ('train_if_multiplier', '1'),
    ]),
]

tensorboard = []
for i, (name, hyper) in enumerate(EXPS):
  tag = '{}_{}_{}'.format(DATE_STR, str(EXP_OFFSET + i).zfill(2), name)
  traindir = os.path.join(TRAINDIR_ROOT, tag)
  gpunum = i
  model_overrides = ','.join(['='.join(h) for h in hyper + EXP_ALL_HYPER])

  trainsh = TRAIN_TEMPL.format(
      gpunum=gpunum,
      traindir=traindir,
      datadir=DATADIR,
      model_overrides=model_overrides)
  with open('{}_train.sh'.format(tag), 'w') as f:
    f.write(trainsh)

  evalsh = EVAL_TEMPL.format(
      traindir=traindir,
      datadir=DATADIR,
      model_overrides=model_overrides)
  with open('{}_eval.sh'.format(tag), 'w') as f:
    f.write(evalsh)

  tensorboard.append((tag, traindir))

tensorboardsh = "tensorboard --host=0.0.0.0 --logdir={}".format(','.join([':'.join(p) for p in tensorboard]))
with open('{}_{}_tb.sh'.format(DATE_STR, str(EXP_OFFSET).zfill(2)), 'w') as f:
  f.write(tensorboardsh)
