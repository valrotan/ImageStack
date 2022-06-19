import subprocess
import sys
import click
import typing


@click.command()
@click.option('--vertical', '-v', 'stack_dir', help='Stack direction', flag_value='vstack')
@click.option('--horizontal', '-h', 'stack_dir', help='Stack direction', flag_value='hstack', default=True)
@click.option('--output', '-o', help='Output file path', type=click.Path())
@click.option('--size', '-s', help='Size of each item in the stack. If 0 all inputs must be same size.',
              type=click.IntRange(0, None), default=0)
@click.option('--fps', '-r', help='Frame rate of the output.',
              type=click.IntRange(1, None), default=30)
@click.option('--ffmpeg', help='FFMPEG executable dir', type=click.Path(), envvar='FFMPEG', default='ffmpeg')
@click.argument('inputs', type=click.Path(exists=True), nargs=-1)
def stack(inputs: typing.List[str], output: str, stack_dir: str, size: int, fps: int, ffmpeg: str):
    exec = ffmpeg
    input = ' '.join(map(lambda s: f'-r {fps} -i {s}', inputs))

    filter = ''
    if size != 0:
        appendage = ''
        for i, inp in enumerate(inputs):
            filter += f'[{i}:v]scale={size}:{size}[scaled{i}];'
            appendage += f'[scaled{i}]'
        filter += appendage

    filter += f'{stack_dir}=inputs={len(inputs)}[out]'
    output_options = f'-map [out] -c:v h264 -pix_fmt yuv420p'
    command = f'{exec} {input} -filter_complex {filter} {output_options} {output} -y'

    args = command.split(' ')
    # print(args)

    process = subprocess.Popen(
        args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr
    )
    out, err = process.communicate()
    retcode = process.poll()
    if retcode:
        raise Exception(out, err)

    return output


if __name__ == '__main__':
    print(stack())
