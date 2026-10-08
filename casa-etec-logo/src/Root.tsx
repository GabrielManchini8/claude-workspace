import {Composition} from 'remotion';
import {CasaETecLogo} from './CasaETecLogo';

export const RemotionRoot: React.FC = () => {
	return (
		<Composition
			id="CasaETecLogo"
			component={CasaETecLogo}
			durationInFrames={150}
			fps={30}
			width={1080}
			height={1080}
		/>
	);
};
