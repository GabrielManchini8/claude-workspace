import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);

// Opcional: usar um Chromium já instalado (ex.: REMOTION_BROWSER=/caminho/headless_shell)
if (process.env.REMOTION_BROWSER) {
	Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
}
