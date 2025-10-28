#!/usr/bin/env python3
#
#
#  IRIS intelowl Source Code
#  Copyright (C) 2022 - dfir-iris
#  contact@dfir-iris.org
#  Created by dfir-iris - 2022-10-29
#
#  License Apache Software License 3.0


import traceback
import copy
from jinja2 import Template

import iris_interface.IrisInterfaceStatus as InterfaceStatus
from app.datamgmt.manage.manage_attribute_db import add_tab_attribute_field

from pyintelowl import IntelOwl, IntelOwlClientException
from time import sleep


class IntelowlHandler(object):
    def __init__(self, mod_config, server_config, logger):
        self.mod_config = mod_config
        self.server_config = server_config
        self.intelowl = self.get_intelowl_instance()
        self.log = logger

    def get_intelowl_instance(self):
        """
        Returns an intelowl API instance depending if the key is premium or not

        :return: IntelOwl Instance
        """
        url = self.mod_config.get('intelowl_url')
        key = self.mod_config.get('intelowl_key')
        should_use_proxy = self.mod_config.get('intelowl_should_use_proxy')
        proxies = {}

        if should_use_proxy is True:
            if self.server_config.get('http_proxy'):
                proxies['https'] = self.server_config.get('HTTPS_PROXY')

            if self.server_config.get('https_proxy'):
                proxies['http'] = self.server_config.get('HTTP_PROXY')

        intelowl = IntelOwl(
            key,
            url,
            certificate=None,
            proxies=proxies
        )

        return intelowl

    def get_playbook_names(self):
        """
        Parse playbook names from config. Supports both single and comma-separated multiple playbooks.

        :return: List of playbook names
        """
        playbook_config = self.mod_config.get("intelowl_playbook_name", "")
        
        # Split by comma and strip whitespace
        playbooks = [name.strip() for name in playbook_config.split(',') if name.strip()]
        
        if not playbooks:
            self.log.warning("No playbook names configured, using default: FREE_TO_USE_ANALYZERS")
            playbooks = ["FREE_TO_USE_ANALYZERS"]
        
        self.log.info(f"Using playbooks: {', '.join(playbooks)}")
        return playbooks

    def prerender_report(self, intelowl_report, playbook_name=None) -> dict:

        pre_render = dict()
        # Deep copy to prevent reference sharing between playbook reports
        pre_render["results"] = copy.deepcopy(intelowl_report)

        analyzer_reports = intelowl_report.get("analyzer_reports")
        connector_reports = intelowl_report.get("connector_reports")

        if analyzer_reports:
            pre_render["nb_analyzer_reports"] = len(analyzer_reports)

        if connector_reports:
            pre_render["nb_connector_reports"] = len(connector_reports)

        iol_report_id = intelowl_report.get("id")
        if iol_report_id:
            iol_report_link = "/".join((self.mod_config.get("intelowl_url").strip("/"), "jobs", str(iol_report_id)))
        else:
            iol_report_link = ""

        pre_render["external_link"] = iol_report_link
        
        # Add playbook name for unique IDs and display in template
        if playbook_name:
            # Create safe ID suffix (remove special chars)
            safe_name = playbook_name.replace(" ", "_").replace("-", "_").replace(".", "_")
            pre_render["playbook_suffix"] = safe_name
            pre_render["playbook_name"] = playbook_name  # For display in template
            self.log.info(f"Generated playbook_suffix: {safe_name} for playbook: {playbook_name}")
        else:
            pre_render["playbook_suffix"] = "default"
            pre_render["playbook_name"] = "Unknown Playbook"
            self.log.warning("No playbook_name provided, using suffix: default")

        return pre_render
    
    def _add_playbook_banner(self, rendered_html: str, playbook_name: str) -> str:
        """
        Add a playbook name banner at the top of the rendered HTML report
        
        :param rendered_html: The rendered HTML content
        :param playbook_name: Name of the playbook used
        :return: HTML with playbook banner prepended
        """
        if not playbook_name or playbook_name == "Unknown Playbook":
            return rendered_html
        
        playbook_banner = f'''
<div class="alert alert-info" role="alert" style="margin-bottom: 20px; border-left: 4px solid #0dcaf0;">
    <h5 class="alert-heading mb-2"><i class="fas fa-book"></i> IntelOwl Playbook</h5>
    <p class="mb-0"><strong>{playbook_name}</strong></p>
</div>
'''
        return playbook_banner + rendered_html

    def gen_domain_report_from_template(self, html_template, intelowl_report, playbook_name=None) -> InterfaceStatus:
        """
        Generates an HTML report for Domain, displayed as an attribute in the IOC

        :param html_template: A string representing the HTML template
        :param intelowl_report: The JSON report fetched with intelowl API
        :param playbook_name: Optional playbook name for unique IDs
        :return: InterfaceStatus
        """
        template = Template(html_template)
        pre_render = self.prerender_report(intelowl_report, playbook_name)

        try:
            rendered = template.render(pre_render)
            # Add playbook name banner
            rendered = self._add_playbook_banner(rendered, playbook_name)

        except Exception:

            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def gen_ip_report_from_template(self, html_template, intelowl_report, playbook_name=None) -> InterfaceStatus:
        """
        Generates an HTML report for IP, displayed as an attribute in the IOC

        :param html_template: A string representing the HTML template
        :param intelowl_report: The JSON report fetched with intelowl API
        :param playbook_name: Optional playbook name for unique IDs
        :return: InterfaceStatus
        """
        template = Template(html_template)
        pre_render = self.prerender_report(intelowl_report, playbook_name)

        try:
            rendered = template.render(pre_render)
            # Add playbook name banner
            rendered = self._add_playbook_banner(rendered, playbook_name)

        except Exception:

            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def gen_url_report_from_template(self, html_template, intelowl_report, playbook_name=None) -> InterfaceStatus:
        """
        Generates an HTML report for URL, displayed as an attribute in the IOC

        :param html_template: A string representing the HTML template
        :param intelowl_report: The JSON report fetched with intelowl API
        :param playbook_name: Optional playbook name for unique IDs
        :return: InterfaceStatus
        """
        template = Template(html_template)
        pre_render = self.prerender_report(intelowl_report, playbook_name)

        try:
            rendered = template.render(pre_render)
            # Add playbook name banner
            rendered = self._add_playbook_banner(rendered, playbook_name)

        except Exception:

            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def gen_hash_report_from_template(self, html_template, intelowl_report, playbook_name=None) -> InterfaceStatus:
        """
        Generates an HTML report for Hash, displayed as an attribute in the IOC

        :param html_template: A string representing the HTML template
        :param intelowl_report: The JSON report fetched with intelowl API
        :param playbook_name: Optional playbook name for unique IDs
        :return: InterfaceStatus
        """
        template = Template(html_template)
        pre_render = self.prerender_report(intelowl_report, playbook_name)

        try:
            rendered = template.render(pre_render)
            # Add playbook name banner
            rendered = self._add_playbook_banner(rendered, playbook_name)

        except Exception:

            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def gen_generic_report_from_template(self, html_template, intelowl_report, playbook_name=None) -> InterfaceStatus:
        """
        Generates an HTML report for Generic ioc, displayed as an attribute in the IOC

        :param html_template: A string representing the HTML template
        :param intelowl_report: The JSON report fetched with intelowl API
        :param playbook_name: Optional playbook name for unique IDs
        :return: InterfaceStatus
        """
        template = Template(html_template)
        pre_render = self.prerender_report(intelowl_report, playbook_name)

        try:
            rendered = template.render(pre_render)
            # Add playbook name banner
            rendered = self._add_playbook_banner(rendered, playbook_name)

        except Exception:

            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        return InterfaceStatus.I2Success(data=rendered)

    def get_job_result(self, job_id):
        """
        Periodically fetches job status until it's finished to get the results

        :param job_id: Union[int, str], The job ID to query
        :return:
        """
        try:
            max_job_time = self.mod_config.get("intelowl_maxtime") * 60
        except Exception:
            self.log.error(traceback.format_exc())
            return InterfaceStatus.I2Error(traceback.format_exc())

        wait_interval = 2

        job_result = self.intelowl.get_job_by_id(job_id)
        status = job_result["status"]

        spent_time = 0
        while (status == "pending" or status == "running") and spent_time <= max_job_time:
            sleep(wait_interval)
            spent_time += wait_interval
            job_result = self.intelowl.get_job_by_id(job_id)
            status = job_result["status"]

        return job_result

    def handle_domain(self, ioc):
        """
        Handles an IOC of type domain and adds IntelOwl insights

        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f'Getting domain report for {ioc.ioc_value}')

        domain = ioc.ioc_value
        playbook_names = self.get_playbook_names()
        
        # Execute analysis for each playbook
        for playbook_name in playbook_names:
            self.log.info(f'Executing playbook: {playbook_name} for domain: {domain}')
            try:
                query_result = self.intelowl.send_observable_analysis_playbook_request(observable_name=domain,
                                                                                       playbook_requested=playbook_name,
                                                                                       tags_labels=["iris"],
                                                                                       observable_classification="domain")
            except IntelOwlClientException as e:
                self.log.error(f"Error executing playbook {playbook_name}: {e}")
                return InterfaceStatus.I2Error(e)

            job_id = query_result.get("job_id")

            try:
                job_result = self.get_job_result(job_id)
            except IntelOwlClientException as e:
                self.log.error(e)
                return InterfaceStatus.I2Error(e)

            if self.mod_config.get('intelowl_report_as_attribute') is True:
                self.log.info(f'Adding new attribute IntelOwl Domain Report to IOC for playbook: {playbook_name}')
                
                # Create a copy to avoid data sharing between playbooks
                report = copy.deepcopy(job_result)
                self.log.info(f'Report for playbook {playbook_name}: job_id={report.get("id")}')

                status = self.gen_domain_report_from_template(self.mod_config.get('intelowl_domain_report_template'),
                                                              report, playbook_name)

                if not status.is_success():
                    return status

                rendered_report = status.get_data()

                try:
                    # Add playbook name to field name if multiple playbooks
                    field_name = f"HTML report - {playbook_name}" if len(playbook_names) > 1 else "HTML report"
                    self.log.info(f"📝 Creating attribute: '{field_name}' for playbook: {playbook_name}")
                    add_tab_attribute_field(ioc, tab_name='IntelOwl Report', field_name=field_name, field_type="html",
                                            field_value=rendered_report)

                except Exception:

                    self.log.error(traceback.format_exc())
                    return InterfaceStatus.I2Error(traceback.format_exc())
            else:
                self.log.info('Skipped adding attribute report. Option disabled')

        return InterfaceStatus.I2Success()

    def handle_ip(self, ioc):
        """
        Handles an IOC of type ip and adds IntelOwl insights

        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f'Getting IP report for {ioc.ioc_value}')

        ip = ioc.ioc_value
        playbook_names = self.get_playbook_names()
        
        # Execute analysis for each playbook
        for playbook_name in playbook_names:
            self.log.info(f'Executing playbook: {playbook_name} for IP: {ip}')
            try:
                query_result = self.intelowl.send_observable_analysis_playbook_request(observable_name=ip,
                                                                                       playbook_requested=playbook_name,
                                                                                       tags_labels=["iris"],
                                                                                       observable_classification="ip")
            except IntelOwlClientException as e:
                self.log.error(f"Error executing playbook {playbook_name}: {e}")
                return InterfaceStatus.I2Error(e)

            job_id = query_result.get("job_id")

            try:
                job_result = self.get_job_result(job_id)
            except IntelOwlClientException as e:
                self.log.error(e)
                return InterfaceStatus.I2Error(e)

            if self.mod_config.get('intelowl_report_as_attribute') is True:
                self.log.info(f'Adding new attribute IntelOwl IP Report to IOC for playbook: {playbook_name}')

                # Create a copy to avoid data sharing between playbooks
                report = copy.deepcopy(job_result)

                status = self.gen_ip_report_from_template(self.mod_config.get('intelowl_ip_report_template'), report, playbook_name)

                if not status.is_success():
                    return status

                rendered_report = status.get_data()

                try:
                    # Add playbook name to field name if multiple playbooks
                    field_name = f"HTML report - {playbook_name}" if len(playbook_names) > 1 else "HTML report"
                    self.log.info(f"📝 Creating attribute: '{field_name}' for playbook: {playbook_name}")
                    add_tab_attribute_field(ioc, tab_name='IntelOwl Report', field_name=field_name, field_type="html",
                                            field_value=rendered_report)

                except Exception:

                    self.log.error(traceback.format_exc())
                    return InterfaceStatus.I2Error(traceback.format_exc())
            else:
                self.log.info('Skipped adding attribute report. Option disabled')

        return InterfaceStatus.I2Success()

    def handle_url(self, ioc):
        """
        Handles an IOC of type URL and adds IntelOwl insights

        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f'Getting URL report for {ioc.ioc_value}')

        url = ioc.ioc_value
        playbook_names = self.get_playbook_names()
        
        # Execute analysis for each playbook
        for playbook_name in playbook_names:
            self.log.info(f'Executing playbook: {playbook_name} for URL: {url}')
            try:
                query_result = self.intelowl.send_observable_analysis_playbook_request(observable_name=url,
                                                                                       playbook_requested=playbook_name,
                                                                                       tags_labels=["iris"],
                                                                                       observable_classification="url")
            except IntelOwlClientException as e:
                self.log.error(f"Error executing playbook {playbook_name}: {e}")
                return InterfaceStatus.I2Error(e)

            job_id = query_result.get("job_id")

            try:
                job_result = self.get_job_result(job_id)
            except IntelOwlClientException as e:
                self.log.error(e)
                return InterfaceStatus.I2Error(e)

            if self.mod_config.get('intelowl_report_as_attribute') is True:
                self.log.info(f'Adding new attribute IntelOwl URL Report to IOC for playbook: {playbook_name}')

                # Create a copy to avoid data sharing between playbooks
                report = copy.deepcopy(job_result)

                status = self.gen_url_report_from_template(self.mod_config.get('intelowl_url_report_template'), report, playbook_name)

                if not status.is_success():
                    return status

                rendered_report = status.get_data()

                try:
                    # Add playbook name to field name if multiple playbooks
                    field_name = f"HTML report - {playbook_name}" if len(playbook_names) > 1 else "HTML report"
                    self.log.info(f"📝 Creating attribute: '{field_name}' for playbook: {playbook_name}")
                    add_tab_attribute_field(ioc, tab_name='IntelOwl Report', field_name=field_name, field_type="html",
                                            field_value=rendered_report)

                except Exception:

                    self.log.error(traceback.format_exc())
                    return InterfaceStatus.I2Error(traceback.format_exc())
            else:
                self.log.info('Skipped adding attribute report. Option disabled')

        return InterfaceStatus.I2Success()

    def handle_hash(self, ioc):
        """
        Handles an IOC of type hash and adds IntelOwl insights

        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f'Getting hash report for {ioc.ioc_value}')

        hash = ioc.ioc_value
        playbook_names = self.get_playbook_names()
        
        # Execute analysis for each playbook
        for playbook_name in playbook_names:
            self.log.info(f'Executing playbook: {playbook_name} for hash: {hash}')
            try:
                query_result = self.intelowl.send_observable_analysis_playbook_request(observable_name=hash,
                                                                                       playbook_requested=playbook_name,
                                                                                       tags_labels=["iris"],
                                                                                       observable_classification="hash")
            except IntelOwlClientException as e:
                self.log.error(f"Error executing playbook {playbook_name}: {e}")
                return InterfaceStatus.I2Error(e)

            job_id = query_result.get("job_id")

            try:
                job_result = self.get_job_result(job_id)
            except IntelOwlClientException as e:
                self.log.error(e)
                return InterfaceStatus.I2Error(e)

            if self.mod_config.get('intelowl_report_as_attribute') is True:
                self.log.info(f'Adding new attribute IntelOwl hash Report to IOC for playbook: {playbook_name}')

                # Create a copy to avoid data sharing between playbooks
                report = copy.deepcopy(job_result)

                status = self.gen_hash_report_from_template(self.mod_config.get('intelowl_hash_report_template'), report, playbook_name)

                if not status.is_success():
                    return status

                rendered_report = status.get_data()

                try:
                    # Add playbook name to field name if multiple playbooks
                    field_name = f"HTML report - {playbook_name}" if len(playbook_names) > 1 else "HTML report"
                    self.log.info(f"📝 Creating attribute: '{field_name}' for playbook: {playbook_name}")
                    add_tab_attribute_field(ioc, tab_name='IntelOwl Report', field_name=field_name, field_type="html",
                                            field_value=rendered_report)

                except Exception:

                    self.log.error(traceback.format_exc())
                    return InterfaceStatus.I2Error(traceback.format_exc())
            else:
                self.log.info('Skipped adding attribute report. Option disabled')

        return InterfaceStatus.I2Success()

    def handle_generic(self, ioc):
        """
        Handles an IOC of type generic and adds IntelOwl insights

        :param ioc: IOC instance
        :return: IIStatus
        """

        self.log.info(f'Getting generic report for {ioc.ioc_value}')

        generic = ioc.ioc_value
        playbook_names = self.get_playbook_names()
        
        # Execute analysis for each playbook
        for playbook_name in playbook_names:
            self.log.info(f'Executing playbook: {playbook_name} for generic: {generic}')
            try:
                query_result = self.intelowl.send_observable_analysis_playbook_request(observable_name=generic,
                                                                                       playbook_requested=playbook_name,
                                                                                       tags_labels=["iris"],
                                                                                       observable_classification="generic")
            except IntelOwlClientException as e:
                self.log.error(f"Error executing playbook {playbook_name}: {e}")
                return InterfaceStatus.I2Error(e)

            job_id = query_result.get("job_id")

            try:
                job_result = self.get_job_result(job_id)
            except IntelOwlClientException as e:
                self.log.error(e)
                return InterfaceStatus.I2Error(e)

            if self.mod_config.get('intelowl_report_as_attribute') is True:
                self.log.info(f'Adding new attribute IntelOwl generic Report to IOC for playbook: {playbook_name}')

                # Create a copy to avoid data sharing between playbooks
                report = copy.deepcopy(job_result)

                status = self.gen_generic_report_from_template(self.mod_config.get('intelowl_generic_report_template'),
                                                               report, playbook_name)

                if not status.is_success():
                    return status

                rendered_report = status.get_data()

                try:
                    # Add playbook name to field name if multiple playbooks
                    field_name = f"HTML report - {playbook_name}" if len(playbook_names) > 1 else "HTML report"
                    self.log.info(f"📝 Creating attribute: '{field_name}' for playbook: {playbook_name}")
                    add_tab_attribute_field(ioc, tab_name='IntelOwl Report', field_name=field_name, field_type="html",
                                            field_value=rendered_report)

                except Exception:

                    self.log.error(traceback.format_exc())
                    return InterfaceStatus.I2Error(traceback.format_exc())
            else:
                self.log.info('Skipped adding attribute report. Option disabled')

        return InterfaceStatus.I2Success()
