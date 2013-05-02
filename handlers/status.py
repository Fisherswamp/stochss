try:
  import json
except ImportError:
  from django.utils import simplejson as json

from collections import OrderedDict
import logging
import traceback
import __future__
import time

from google.appengine.ext import db

import os
from stochssapp import BaseHandler
from stochss.backendservice import *
from backend.backendservice import backendservices

import shutil

class StatusPage(BaseHandler):
    
    def get(self):
        #all_urls = self.get_all_urls()
        context = self.getContext()
        self.render_response('status.html', **context)
        
    def post(self):
        
        params = self.request.POST
        
        if 'delete' in params:
            # The jobs to delete are specified in the checkboxes 
            print "Deleting selected elements"
            jobs_to_delete = params.getall('select_job')
            
            service = backendservices()

            # Select the jobs to delete from the datastore
            result = {}
            for job_name in jobs_to_delete:
                try:
                    job = db.GqlQuery("SELECT * FROM StochKitJobWrapper WHERE user_id = :1 AND name = :2", self.user.user_id(),job_name).get()
                    stochkit_job = job.stochkit_job
                except Exception,e:
                    result = {'status':False,'msg':"Could not retreive the jobs"+job_name+ " from the datastore."}
        
                # TODO: Call the backend to kill and delete the job and all associated files from EC2/local storage.
                try:
                    service.deleteTaskLocal([stochkit_job.pid])
                    isdeleted_backend = True
                except Exception,e:
                    isdeleted_backend = False
                    result['status']=False
                    result['msg'] = "Failed to kill task with PID " + str(stochkit_job.pid) + str(e)
                        
                if isdeleted_backend:
                    # Delete all the files and delete the job from the datastore
                    try:
                        # We remove the local entry of the job output directory
                        shutil.rmtree(stochkit_job.output_location)
                        # TODO: Check if it is a Cloud job, and in that case call the
                        # backend to clean up all files from the remote end.
                        db.delete(job)
                    except Exception,e:
                        result = {'status':False,'msg':"Failed to delete job "+job_name}

            # Render the page
                            
            # AH: This is a hack to prevent the page from reloading before the datastore transactions
            # have taken place. I think it is only necessary for the SQLLite backend stub.
            # TODO: We need a better way to check if the entities are gone from the datastore...
            time.sleep(0.5)
            context = self.getContext()
            self.render_response('status.html', **dict(result,**context))
                
        elif 'refresh' in params:
            # Get the context and reload the page
            context = self.getContext()
            self.render_response('status.html', **context)
        else:
            context = self.getContext()
            result = {'status':False,'msg':"There was an error processing the request."}
            self.render_response('status.html', **dict(result,**context))
    
    def getContext(self):
        """ 
            Get information about all the jobs that exist in the system and assemble a dict
            with info to display on the page. 
        """
        context = {}
        result = {}
        service = backendservices()
        # Grab references to all the user's StochKitJobs in the system
        all_stochkit_jobs = db.GqlQuery("SELECT * FROM StochKitJobWrapper WHERE user_id = :1", self.user.user_id())
        if all_stochkit_jobs == None:
            context['no_jobs'] = 'There are no jobs in the system.'
        else:
            # We want to display the name of the job, the status of the Job, and if it is
            # completed, the URL where the user can download the output.
            all_jobs = []
            for job in all_stochkit_jobs.run():
                
                # Get the job id
                stochkit_job = job.stochkit_job
                
                # Query the backend for the status of the job, but only if the current status is not Finished
                if not stochkit_job.status == "Finished":
                    try:
                        if stochkit_job.resource == 'Local':
                            # First, check if the job is still running
                            res = service.checkTaskStatusLocal([stochkit_job.pid])
                            if res[stochkit_job.pid]:
                                stochkit_job.status = "Running"
                            else:
                                # Check if the output folder is present, in which case the job finsihed sucessfully.
                                if os.path.exists(stochkit_job.output_location+"/result"):
                                    stochkit_job.status = "Finished"
                                else:
                                    stochkit_job.status = "Failed"
                        elif stochkit_job.resource == 'Cloud':
                            # Retrive credentials from the datastore
                            
                            # Check the status on the remote end
                            taskparams = {'AWS_ACCESS_KEY_ID':db_credentials.access_key,'AWS_SECRET_ACCESS_KEY':db_credentials.secret_key,'taskids':[stochkit_job.pid]}
                            status = service.describeTask(taskparams)
                            print status
                
                        # Todo, implement check in the case of Cloud
                    except Exception,e:
                        result = {'status':False,'msg':'Could not determine the status of the jobs.'+str(e)}
                
                all_jobs.append(stochkit_job)
                # Save changes to the status
                job.put()
                #job_status.append(self.getJobStatus(task_id))
                
        context['all_jobs']=all_jobs
    
        return dict(result,**context)

    def getJobStatus(self,task_id):
        # TODO: request the status from the backend.
        return True

    def get_all_urls(self):
        """
            Get the URLs of 
        """
        model = self.get_session_property('model_edited')
        if model is None:
            return None
        else:
        	result = backendservice.describeTask(valid_username)
		self.render_response('status.html', **result)


class JobOutPutPage(BaseHandler):

    def get(self):
        """ Well, I am not sure what to do here... """
        context,result = self.getContext()
        self.render_response('stochkitjoboutputpage.html',**dict(result,**context))

    def post(self):
        self.response.out.write("POST")

    def getContext(self):
        params = self.request.POST
        params = dict(params,**self.request.GET)

        job_name = params['job_name']
        context={}
        result = {}
        context['job_name']=job_name
        
        # Grab the Job from the datastore
        try:
            job = db.GqlQuery("SELECT * FROM StochKitJobWrapper WHERE user_id = :1 AND name = :2", self.user.user_id(),job_name).get()
            stochkit_job = job.stochkit_job
            context['stochkit_job']=stochkit_job
        except Exception,e:
            result = {'status':False,'msg':"Could not retreive the jobs"+job_name+ " from the datastore."}
        
        # Check if the results and stats folders are present locally
        if os.path.exists(stochkit_job.output_location+"/result"):
            context['local_data']=True
        if os.path.exists(stochkit_job.output_location+"/result/stats"):
            context['local_statistics']=True
                
    
        return context,result



