import { useTranslation } from "react-i18next";

const PrivacyPolicy = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 text-primary">
      <h1 className="text-3xl font-bold mb-6">
        {t("legal.privacy_policy.title")}
      </h1>
      <p className="mb-4">{t("legal.privacy_policy.updated")}</p>

      <div className="prose dark:prose-invert max-w-none">
        {/* Intro */}
        <p className="mb-4">{t("legal.privacy_policy.intro_1")}</p>
        <p className="mb-4">{t("legal.privacy_policy.intro_2")}</p>

        {/* Definitions */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.definitions.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.definitions.desc")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.definitions.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </ul>

        {/* Collection */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.collection.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.collection.desc")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.collection.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        {/* Usage */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.usage.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.usage.desc")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.usage.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        {/* Third Party End User */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.third_party_end_user.title")}
        </h2>
        <p className="mb-4">
          {t("legal.privacy_policy.third_party_end_user.p1")}
        </p>
        <p className="mb-4">
          {t("legal.privacy_policy.third_party_end_user.p2")}
        </p>

        {/* Third Party Customer */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.third_party_customer.title")}
        </h2>
        <p className="mb-4">
          {t("legal.privacy_policy.third_party_customer.p1")}
        </p>

        {/* Sharing */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.sharing.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.sharing.p1")}</p>

        {/* Collection Source */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.collection_source.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.collection_source.p1")}</p>

        {/* Email Usage */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.email_usage.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.email_usage.p1")}</p>

        {/* Retention */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.retention.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.retention.p1")}</p>

        {/* Protection */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.protection.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.protection.p1")}</p>

        {/* International */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.international.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.international.p1")}</p>

        {/* Security Note */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.security_note.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.security_note.p1")}</p>

        {/* Update Info */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.update_info.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.update_info.p1")}</p>

        {/* Sale of Business */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.sale_business.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.sale_business.p1")}</p>

        {/* Affiliates */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.affiliates.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.affiliates.p1")}</p>

        {/* Governing Law */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.governing_law.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.governing_law.p1")}</p>

        {/* Consent */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.consent.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.consent.p1")}</p>

        {/* Links */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.links.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.links.p1")}</p>

        {/* Cookies */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.cookies.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.cookies.p1")}</p>

        {/* Blocking Cookies */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.blocking_cookies.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.blocking_cookies.p1")}</p>

        {/* Payment */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.payment.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.payment.p1")}</p>

        {/* Kids */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.kids.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.kids.p1")}</p>

        {/* Tracking Tech */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.tracking.title")}
        </h2>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.tracking.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li
              key={index}
              className="mb-2"
              dangerouslySetInnerHTML={{ __html: item }}
            />
          ))}
        </ul>

        {/* GDPR */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.gdpr.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.gdpr.p1")}</p>

        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.gdpr.sub_title_1")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.gdpr.p2")}</p>

        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.gdpr.sub_title_2")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.gdpr.p3")}</p>
        <p className="mb-4">{t("legal.privacy_policy.gdpr.p4")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.gdpr.list_principles", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.gdpr.sub_title_3")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.gdpr.p5")}</p>
        <p className="mb-4">{t("legal.privacy_policy.gdpr.p6")}</p>

        {/* California CCPA */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.california.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.california.p1")}</p>
        <p className="mb-4">{t("legal.privacy_policy.california.p2")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.california.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
        <p className="mb-4">{t("legal.privacy_policy.california.p3")}</p>
        <p className="mb-4">{t("legal.privacy_policy.california.p4")}</p>
        <p className="mb-4">{t("legal.privacy_policy.california.p5")}</p>

        {/* California CalOPPA */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.caloppa.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.caloppa.p1")}</p>
        <p className="mb-4">{t("legal.privacy_policy.caloppa.p2")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.privacy_policy.caloppa.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
        <p className="mb-4">{t("legal.privacy_policy.caloppa.p3")}</p>
        <p className="mb-4">{t("legal.privacy_policy.caloppa.p4")}</p>
        <p className="mb-4">{t("legal.privacy_policy.caloppa.p5")}</p>

        {/* Contact */}
        <h2 className="text-xl font-bold mt-6 mb-4">
          {t("legal.privacy_policy.contact.title")}
        </h2>
        <p className="mb-4">{t("legal.privacy_policy.contact.p1")}</p>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
