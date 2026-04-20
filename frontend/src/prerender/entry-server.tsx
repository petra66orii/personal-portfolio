import { renderToString } from "react-dom/server";
import { Helmet } from "react-helmet";
import { StaticRouter } from "react-router";
import App from "../App";
import "../index.css";
import "../i18n.prerender";

type HelmetTags = {
  title: string;
  meta: string;
  link: string;
  script: string;
};

export function render(url: string): { appHtml: string; helmet: HelmetTags } {
  const appHtml = renderToString(
    <StaticRouter location={url}>
      <App />
    </StaticRouter>,
  );
  const helmet = Helmet.renderStatic();

  return {
    appHtml,
    helmet: {
      title: helmet.title.toString(),
      meta: helmet.meta.toString(),
      link: helmet.link.toString(),
      script: helmet.script.toString(),
    },
  };
}
