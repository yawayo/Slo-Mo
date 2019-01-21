01/07 논문 요약(2/3)
01/07 코드 실행(실패_미숙한 개발 환경_pycharm에서 torch가 import되지 않음->원인 분석중)

01/08 논문 요약(끝)
01/08 코드 실행(진행중)

01/09 video_to_slomo 코드 실행(어제의 실패 원인 : pytorch의 버전이 달라 실행에 실패 -> 버전 변경 후 성공)
01/09 train 코드 실행(실패 -> 원인 분석중)
01/09 Dataset 분석:adobe240(코드 분석하면서 진행하는 중)

01/10 adobe240fps
01/10 length : 각각 다 다름
01/10 width : 1280
01/10 height : 720
01/10 fps : 각각 다 다름
 
01/10 input1		      	output1
01/10 width :  306	 	width :  306
01/10 height :  278		height :  278
01/10 fps :  30.0	  	fps :  25.0

01/10 input2	      		output2
01/10 width :  450	 	width :  450
01/10 height :  600		height :  600
01/10 fps :  6.25	  	fps :  25.0

01/10 input3		      	output3
01/10 width :  1280		width :  1280
01/10 height :  720		height :  720
01/10 fps : 30.0		   fps :  25.0

01/10 input4_6fps	  	output4
01/10 width :  1280		width :  1280
01/10 height :  720		height :  720
01/10 fps : 6.0		   	fps :  25.0

01/10 input4 (1)	   	output4_2
01/10 width :  1280		width :  1280
01/10 height :  720		height :  720
01/10 fps : 2.181164645713842	fps :  25.0

01/10 input5		      	output5
01/10 width :  356	 	width :  356
01/10 height :  480		height :  480
01/10 fps : 3.702127659574468	fps :  25.0

01/10 input6		      	output6
01/10 width :  1280
01/10 height :  720		
01/10 fps :  239.97193310723893	fps :  25.0

01/10 출력 width = 입력 width
01/10 출력 height = 입력 height
01/10 입력 fps : 각각 다 다름
01/10 출력 fps = 설정한 fps
01/11 비디오 속도 = input fps * sf / output fps

01/10 video_to_video 코드로 여러 영상을 돌려본다.(시간이 너무 오래 걸림. 진행중)
01/10 Slo-Mo 코드 분석(진행중)
01/10 Slo-Mo train시키기(보류. 추후에 시간이 나면 실행)

01/11 video_to_video 코드로 여러 영상을 돌려본다.(기상청 홈페이지에 있던 구름 영상도 돌려봄)
01/11 돌린 영상(dataset에 있던 영상(5시간 소요), 기상청 구름 이미지->비디오 변환(6fps->25fps, 4fps->25fps, mp4->mp4, gif->mp4))
01/11 video_to_video 코드 분석

01/14 이미지를 무손실로 비디오로 바꿔주는 방법 찾기(마땅한 플랫폼 없음. ffmpeg 사용)
01/14 video_to_slomo 파라미터 바꿔서 돌려보기(sf, output fps 변경)
01/14 여러 영상 돌려보기(지구영상(3시간 주기의 이미지->결과 안좋음), 한반도 구름영상(30분 주기의 이미지->결과 좋음)

01/15 video_to_slomo 내부 구성 바꿔서 돌려보기(pooling 종류, relu 종류, normalize수 변경)->부질없는짓이였다.
01/15 여러 영상 돌려보기(직접 연사로 찍은 이미지->결과 좋음)
01/15 데이터셋 미확보로 인한 train 보류

01/16 여러 영상 돌려보기(태양영상)
01/16 model 바꿔서 돌려보기(시도중)

01/17 새로운 dataset으로 학습시키기 위해 dataset의 mean과 std 구하기(normalization을 위해)

01/18 새로운 dataset으로 학습시키기(normalization을 위해 dtaset의 mean과 std 구하기, dataset 만들기)

01/19 새로운 dataset 준비하기(create_dataset.py ->ffmpeg의 permission denied -> )
