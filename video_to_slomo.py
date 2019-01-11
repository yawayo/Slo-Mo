#!/usr/bin/env python3
import argparse
import os
import os.path
import ctypes
from shutil import rmtree, move
from PIL import Image
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
import model
import dataloader
import platform
from tqdm import tqdm

# 명령 실행 시 지정해야 되는 항목들
parser = argparse.ArgumentParser()
parser.add_argument("--ffmpeg_dir", type=str, default="", help='ffmpeg.exe의 경로')
parser.add_argument("--video", type=str, required=True, help='변환할 비디오의 경로')
parser.add_argument("--checkpoint", type=str, required=True, help='사전학습된 모델의 체크포인트 경로')
parser.add_argument("--fps", type=float, default=30, help='출력되는 비디오의 fps 지정. Default: 30.')
parser.add_argument("--sf", type=int, required=True, help='slomo factor N 지정. Nx만큼 프레임이 증가. 예) sf=2 ==> 2x frames')
parser.add_argument("--batch_size", type=int, default=1, help='빠른 변환을 위한 batch size 지정. cpu/gpu 메모리에 따라 달라진다. Default: 1')
parser.add_argument("--output", type=str, default="output.mp4", help='출력되는 비디오의 이름 지정. Default: output.mp4')
args = parser.parse_args()

def check():
    """
    실행 시 지정한 항목들의 유효성 검사.

    Parameters
    ----------
        None

    Returns
    -------
        error : string
            오류 발생 시 오류 메시지, 그렇지 않으면 빈 문자열.
    """


    error = ""
    if (args.sf < 2):
        error = "Error: --sf/slomo factor 는 2 이상이어야 한다"
    if (args.batch_size < 1):
        error = "Error: --batch_size 는 1 이상이어야 한다"
    if (args.fps < 1):
        error = "Error: --fps 는 1 이상이어야 한다"
    return error

def extract_frames(video, outDir):
    """
    비디오에서 이미지로 변환.

    Parameters
    ----------
        video : string
            비디오 파일의 전체 경로.
        outDir : string
            추출된 이미지를 출력하기 위한 디렉터리 경로.

    Returns
    -------
        error : string
            오류 발생 시 오류 메시지, 그렇지 않으면 빈 문자열.
    """


    error = ""
    print('{} -i {} -vsync 0 -qscale:v 2 {}/%06d.jpg'.format(os.path.join(args.ffmpeg_dir, "ffmpeg"), video, outDir))
    #-i : Input   -vsync : 비디오 동기화 방법   -qscale : 고정된 양자화 비율 사용
    retn = os.system('{} -i {} -vsync 0 -qscale:v 2 {}/%06d.jpg'.format(os.path.join(args.ffmpeg_dir, "ffmpeg"), video, outDir)
    #-i : Input   -vsync : 비디오 동기화 방법   -qscale : 고정된 양자화 비율 사용)
    if retn:
        error = "파일 변환 에러:{}. Exiting.".format(video)
    return error

def create_video(dir):
    error = ""
    print('{} -r {} -i {}/%d.jpg -qscale:v 2 {}'.format(os.path.join(args.ffmpeg_dir, "ffmpeg"), args.fps, dir, args.output))
    retn = os.system('{} -r {} -i {}/%d.jpg -crf 17 -vcodec libx264 {}'.format(os.path.join(args.ffmpeg_dir, "ffmpeg"), args.fps, dir, args.output))
    #-r :  Frame Rate   -i : Input   -qscale : 고정된 양자화 비율 사용   -crf :  화질을 설정   -vcodec : 비디오 코덱, 압축
    if retn:
        error = "출력 비디오 생성 에러. 종료합니다."
    return error


def main():
    # Check if arguments are okay
    error = check()                                     #에러 체크
    if error:                                           #에러가 있으면
        print(error)                                    #에러 종류 출력
        exit(1)                                         #종료

    #추출 폴더 생성 및 추출 프레임
    IS_WINDOWS = 'Windows' == platform.system()         #OS 종류가 윈도우면
    extractionDir = "tmpSuperSloMo"
    if not IS_WINDOWS:
        # Assuming UNIX-like system where "." indicates hidden directories
        extractionDir = "." + extractionDir             #숨겨진 파일 경로로 변경
    if os.path.isdir(extractionDir):                    #이미 directory가 존재하는지 확인
        rmtree(extractionDir)                           #존재하면 삭제
    os.mkdir(extractionDir)                             #새로운 directory 생성
    if IS_WINDOWS:                                      #OS가 윈도우이면
        FILE_ATTRIBUTE_HIDDEN = 0x02                    #숨김파일
        # ctypes.windll only exists on Windows
        ctypes.windll.kernel32.SetFileAttributesW(extractionDir, FILE_ATTRIBUTE_HIDDEN)     #숨겨진 파일 생성

    extractionPath = os.path.join(extractionDir, "input")   #새로운 경로 설정
    outputPath     = os.path.join(extractionDir, "output")  #새로운 경로 설정
    os.mkdir(extractionPath)                                #새로운 경로 생성
    os.mkdir(outputPath)                                    #새로운 경로 생성
    error = extract_frames(args.video, extractionPath)      #비디오를 읽어들이는데
    if error:                                               #에러가 있으면
        print(error)                                        #에러 출력
        exit(1)

    # device 설정
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    #Nomalization
    mean = [0.429, 0.431, 0.397]
    std  = [1, 1, 1]
    normalize = transforms.Normalize(mean=mean,
                                     std=std)
    #ReNomalization
    negmean = [x * -1 for x in mean]
    revNormalize = transforms.Normalize(mean=negmean, std=std)

    # Temporary fix for issue #7 https://github.com/avinashpaliwal/Super-SloMo/issues/7 -
    # - Removed per channel mean subtraction for CPU.
    if (device == "cpu"):
        transform = transforms.Compose([transforms.ToTensor()])
        TP = transforms.Compose([transforms.ToPILImage()])
    else:
        transform = transforms.Compose([transforms.ToTensor(), normalize])
        TP = transforms.Compose([revNormalize, transforms.ToPILImage()])

    # 데이터 로드
    videoFrames = dataloader.Video(root=extractionPath, transform=transform)
    videoFramesloader = torch.utils.data.DataLoader(videoFrames, batch_size=args.batch_size, shuffle=False)

    # 모델 초기화
    flowComp = model.UNet(6, 4)
    flowComp.to(device)
    for param in flowComp.parameters():
        param.requires_grad = False #학습하지 않음
    ArbTimeFlowIntrp = model.UNet(20, 5)
    ArbTimeFlowIntrp.to(device)
    for param in ArbTimeFlowIntrp.parameters():
        param.requires_grad = False #학습하지 않음
    
    flowBackWarp = model.backWarp(videoFrames.dim[0], videoFrames.dim[1], device)   #이미지의 width height
    flowBackWarp = flowBackWarp.to(device)      #

    dict1 = torch.load(args.checkpoint, map_location='cpu')
    ArbTimeFlowIntrp.load_state_dict(dict1['state_dictAT'])
    flowComp.load_state_dict(dict1['state_dictFC'])

    # Interpolate frames
    frameCounter = 1

    with torch.no_grad():   #학습하지 않음
        for _, (frame0, frame1) in enumerate(tqdm(videoFramesloader), 0):

            I0 = frame0.to(device)
            I1 = frame1.to(device)

            flowOut = flowComp(torch.cat((I0, I1), dim=1))
            F_0_1 = flowOut[:,:2,:,:]
            F_1_0 = flowOut[:,2:,:,:]

            # Save reference frames in output folder
            for batchIndex in range(args.batch_size):
                (TP(frame0[batchIndex].detach())).resize(videoFrames.origDim, Image.BILINEAR).save(os.path.join(outputPath, str(frameCounter + args.sf * batchIndex) + ".jpg"))
            frameCounter += 1

            # Generate intermediate frames
            for intermediateIndex in range(1, args.sf):
                t = intermediateIndex / args.sf
                temp = -t * (1 - t)
                fCoeff = [temp, t * t, (1 - t) * (1 - t), temp]

                F_t_0 = fCoeff[0] * F_0_1 + fCoeff[1] * F_1_0
                F_t_1 = fCoeff[2] * F_0_1 + fCoeff[3] * F_1_0

                g_I0_F_t_0 = flowBackWarp(I0, F_t_0)
                g_I1_F_t_1 = flowBackWarp(I1, F_t_1)
                
                intrpOut = ArbTimeFlowIntrp(torch.cat((I0, I1, F_0_1, F_1_0, F_t_1, F_t_0, g_I1_F_t_1, g_I0_F_t_0), dim=1))
                    
                F_t_0_f = intrpOut[:, :2, :, :] + F_t_0
                F_t_1_f = intrpOut[:, 2:4, :, :] + F_t_1
                V_t_0   = F.sigmoid(intrpOut[:, 4:5, :, :])
                V_t_1   = 1 - V_t_0
                    
                g_I0_F_t_0_f = flowBackWarp(I0, F_t_0_f)
                g_I1_F_t_1_f = flowBackWarp(I1, F_t_1_f)
                
                wCoeff = [1 - t, t]

                Ft_p = (wCoeff[0] * V_t_0 * g_I0_F_t_0_f + wCoeff[1] * V_t_1 * g_I1_F_t_1_f) / (wCoeff[0] * V_t_0 + wCoeff[1] * V_t_1)

                # Save intermediate frame
                for batchIndex in range(args.batch_size):
                    (TP(Ft_p[batchIndex].cpu().detach())).resize(videoFrames.origDim, Image.BILINEAR).save(os.path.join(outputPath, str(frameCounter + args.sf * batchIndex) + ".jpg"))
                frameCounter += 1
            
            # Set counter accounting for batching of frames
            frameCounter += args.sf * (args.batch_size - 1)

    # Generate video from interpolated frames
    create_video(outputPath)

    # Remove temporary files
    rmtree(extractionDir)

    exit(0)

main()
