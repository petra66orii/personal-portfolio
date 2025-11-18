import { useTranslation } from "react-i18next";

const TermsOfUse = () => {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 text-primary">
      <h1 className="text-3xl font-bold mb-6">
        {t("legal.terms_of_use.title")}
      </h1>
      <p className="mb-4">{t("legal.terms_of_use.updated")}</p>

      <div className="prose dark:prose-invert max-w-none">
        {/* Intro */}
        <p className="mb-4">{t("legal.terms_of_use.intro.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.intro.p2")}</p>
        <p
          className="mb-4"
          dangerouslySetInnerHTML={{ __html: t("legal.terms_of_use.intro.p3") }}
        />

        {/* License */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.license.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.license.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.license.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.license.p3")}</p>

        {/* Definitions */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.definitions.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.definitions.p1")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.terms_of_use.definitions.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index} dangerouslySetInnerHTML={{ __html: item }} />
          ))}
        </ul>

        {/* Restrictions */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.restrictions.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.restrictions.p1")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.terms_of_use.restrictions.list", {
              returnObjects: true,
            }) as string[]
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        {/* Refunds */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.refunds.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.refunds.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.refunds.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.refunds.p3")}</p>

        {/* Suggestions */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.suggestions.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.suggestions.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.suggestions.p2")}</p>

        {/* Consent */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.consent.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.consent.p1")}</p>

        {/* Links */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.links.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.links.p1")}</p>

        {/* Cookies */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.cookies.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.cookies.p1")}</p>

        {/* Changes */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.changes.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.changes.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.changes.p2")}</p>

        {/* Modifications */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.modifications.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.modifications.p1")}</p>

        {/* Updates */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.updates.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.updates.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.updates.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.updates.p3")}</p>

        {/* Third Party */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.third_party.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.third_party.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.third_party.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.third_party.p3")}</p>

        {/* Termination */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.termination.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.termination.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.termination.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.termination.p3")}</p>
        <p className="mb-4">{t("legal.terms_of_use.termination.p4")}</p>
        <p className="mb-4">{t("legal.terms_of_use.termination.p5")}</p>

        {/* Copyright */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.copyright.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.copyright.p1")}</p>

        {/* Indemnification */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.indemnification.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.indemnification.p1")}</p>

        {/* Warranties */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.warranties.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.warranties.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.warranties.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.warranties.p3")}</p>

        {/* Liability */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.liability.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.liability.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.liability.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.liability.p3")}</p>

        {/* Severability */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.severability.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.severability.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.severability.p2")}</p>

        {/* Waiver */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.waiver.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.waiver.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.waiver.p2")}</p>

        {/* Amendments */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.amendments.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.amendments.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.amendments.p2")}</p>

        {/* Entire Agreement */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.entire_agreement.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.entire_agreement.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.entire_agreement.p2")}</p>

        {/* Updates Terms */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.updates_terms.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.updates_terms.p1")}</p>

        {/* IP */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.ip.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.ip.p1")}</p>

        {/* Arbitration */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.arbitration.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.arbitration.p1")}</p>

        {/* Notice Dispute */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.notice_dispute.title")}
        </h1>
        <p
          className="mb-4"
          dangerouslySetInnerHTML={{
            __html: t("legal.terms_of_use.notice_dispute.p1"),
          }}
        />

        {/* Binding Arbitration */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.binding_arbitration.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.binding_arbitration.p1")}</p>

        {/* Submissions */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.submissions.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.submissions.p1")}</p>

        {/* Promotions */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.promotions.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.promotions.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.promotions.p2")}</p>

        {/* Typos */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.typos.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.typos.p1")}</p>

        {/* Miscellaneous */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.miscellaneous.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.miscellaneous.p1")}</p>

        {/* Disclaimer */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.disclaimer.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.disclaimer.p1")}</p>
        <p className="mb-4">{t("legal.terms_of_use.disclaimer.p2")}</p>
        <p className="mb-4">{t("legal.terms_of_use.disclaimer.p3")}</p>
        <p className="mb-4">{t("legal.terms_of_use.disclaimer.p4")}</p>

        {/* Contact */}
        <h1 className="text-3xl font-bold mb-6">
          {t("legal.terms_of_use.contact.title")}
        </h1>
        <p className="mb-4">{t("legal.terms_of_use.contact.p1")}</p>
        <ul className="list-disc pl-5 mb-4">
          {(
            t("legal.terms_of_use.contact.list", {
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

export default TermsOfUse;
