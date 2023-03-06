import { Request } from "express";
import config from "config";
import nodemailer from "nodemailer";
import * as path from "path";
import * as fs from "fs";
import * as eta from "eta"; // HTML templating engine

const SERVER: string = config.get("server.smtp.server");
const PORT: number = config.get("server.smtp.port");
const FROM: string = config.get("server.smtp.senderAddress");
const INNKEEPER: string = config.get("server.smtp.innkeeperInbox");

/**
 * @function sendConfirmationEmail
 * Send the preconfigured emails when a reservation is created
 * @returns {string} The inkeeper token
 */
export const sendConfirmationEmail = async (req: Request) => {
  console.log("sendConfirmationEmail", req.body);
  try {
    const transporter = nodemailer.createTransport({
      host: SERVER,
      port: PORT,
      secure: false,
    });

    /**
     * Render the HTML template for the tenant
     */
    const tenantHtmlTemplate = fs.readFileSync(
      path.join(__dirname, "email_templates/reservation_received_tenant.html"),
      "utf8"
    );
    const tenantHtml = eta.render(tenantHtmlTemplate, req);

    // Send a confirmation email to the person doing the reservation
    await transporter.sendMail({
      from: FROM,
      to: req.body.contactEmail,
      subject: "Your reservation details",
      html: tenantHtml, // html body
    });

    /**
     * Render the HTML template for the innkeeper
     */
    const innkeeperHtmlTemplate = fs.readFileSync(
      path.join(
        __dirname,
        "email_templates/reservation_received_innkeeper.html"
      ),
      "utf8"
    );
    const innkeeperHtml = eta.render(innkeeperHtmlTemplate, req);

    // Send a notification email to the Innkeeper team
    await transporter.sendMail({
      from: FROM,
      // to: INNKEEPER,
      to: "popkinj@gmail.com",
      subject: "New tenant reservation",
      html: innkeeperHtml, // html body
    });
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};

/**
 * @function sendStatusEmail
 * Send the preconfigured emails as part of the reservation flow
 * @returns {string} The inkeeper token
 */
export const sendStatusEmail = async (req: Request) => {
  try {
    const transporter = nodemailer.createTransport({
      host: SERVER,
      port: PORT,
      secure: false,
    });

    console.log("sendStatusEmail", req.body);
    const templateUrl = req.body.state.match(/approved/i)
      ? "reservation_approved_tenant.html"
      : "reservation_declined_tenant.html";

    /**
     * Render the HTML template for the tenant
     */
    const tenantHtmlTemplate = fs.readFileSync(
      path.join(__dirname, `email_templates/${templateUrl}`),
      "utf8"
    );
    const tenantHtml = eta.render(tenantHtmlTemplate, req);

    // Send a status update email to the applicant
    await transporter.sendMail({
      from: FROM,
      to: req.body.contactEmail,
      subject: "Your reservation details",
      html: tenantHtml, // html body
    });
  } catch (error) {
    console.error(`Error sending email: ${error}`);
    throw error;
  }
};
