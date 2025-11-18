import { useTranslation } from "react-i18next";

const CookiePolicy = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 text-primary">
      <h1 className="text-3xl font-bold mb-6">
        {t("legal.cookie_policy.title")}
      </h1>
      <p className="mb-4">{t("legal.cookie_policy.updated")}</p>

      <div className="prose dark:prose-invert max-w-none">
        {/* Definitions */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.definitions.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.definitions.p1")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.cookie_policy.definitions.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </ul>
        <p
          className="mb-4"
          dangerouslySetInnerHTML={{
            __html: t("legal.cookie_policy.definitions.termify_note"),
          }}
        />

        {/* Introduction */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.intro.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.intro.p1")}</p>

        {/* What is a cookie */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.what_is.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.what_is.p1")}</p>

        {/* Why do we use cookies */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.why_use.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.why_use.p1")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.cookie_policy.why_use.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        {/* Types of Cookies */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.types.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.types.p1")}</p>
        <p className="mb-4">{t("legal.cookie_policy.types.p2")}</p>
        <p className="mb-4">{t("legal.cookie_policy.types.p3")}</p>

        {/* Essential */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.essential.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.essential.p1")}</p>

        {/* Performance */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.performance.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.performance.p1")}</p>

        {/* Analytics */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.analytics.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.analytics.p1")}</p>
        <p className="mb-4">{t("legal.cookie_policy.analytics.p2")}</p>

        {/* Third Party */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.third_party.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.third_party.p1")}</p>

        {/* Management */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.management.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.management.p1")}</p>
        <p className="mb-4">{t("legal.cookie_policy.management.p2")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.cookie_policy.management.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        {/* Blocking */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.blocking.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.blocking.p1")}</p>

        {/* Changes */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.changes.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.changes.p1")}</p>

        {/* Consent */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.consent.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.consent.p1")}</p>

        {/* Contact */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.cookie_policy.contact.title")}
        </h1>
        <p className="mb-4">{t("legal.cookie_policy.contact.p1")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.cookie_policy.contact.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </ul>

        <script
          data-cfasync="false"
          src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"
        ></script>
      </div>
    </div>
  );
};

export default CookiePolicy;
