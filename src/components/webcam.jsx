import Webcam from "react-webcam";

function WebcamComponent() {
  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user",
    aspectRatio: 4/3,
    advanced: [
      {
        zoom: 0.1,
        digitalZoom: 0.1,
      }
    ]
  };

  return (
    <div className="webcam-wrapper">
      <Webcam
        audio={false}
        width="100%"
        height="100%"
        videoConstraints={videoConstraints}
        mirrored={true}
        screenshotFormat="image/jpeg"
      />
    </div>
  );
}

export default WebcamComponent;