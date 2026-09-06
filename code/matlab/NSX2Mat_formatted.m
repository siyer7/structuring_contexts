% NSX2Mat_byID.m  (drop next to your code and run this instead)
addpath(genpath('/home/nuttidalab/Documents/OSort/osort-v4-code/code/continuous/blackrock'));

% CHANGES WITH PATIENT
subj = '202601';
if strcmp(subj, '202512') % only for 1st patient with old recording system
    rawNSX  = sprintf('../../data/%s/raw/datafile_202512b002.ns6', subj);
else
    rawDir = sprintf('../../data/%s/raw/', subj);
    d = dir(fullfile(rawDir, '*.ns6'));
    assert(~isempty(d), 'No .ns6 files found');
    rawNSX = fullfile(rawDir, d(1).name);
end

% create dir if it doesnt exist
outDir = fullfile('..','..','data', subj, 'osort_mat', 'nsx2mat');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end
prefix = 'BL';


if ~exist(outDir,'dir'); mkdir(outDir); end

% 1) Read header and get true ChannelIDs
NS6hdr   = openNSx(rawNSX, 'noread');
chanIDs  = NS6hdr.MetaTags.ChannelID(:)';   % e.g., [2 4 7 ...]
nEnabled = numel(chanIDs); % no. of channels

% 2) Loop over ChannelIDs, find their *index*, read just that channel
for ii = 1:nEnabled
    thisID  = chanIDs(ii);                   % original Blackrock ChannelID
    idx     = ii;                            % index in the enabled list (1..nEnabled)

    % read only this index; units in microvolts
    NS6 = openNSx(rawNSX, 'read', 'uV', ['c:' num2str(idx)]);

    % NS6.Data: 1 x T; ensure row vector
    data = double(NS6.Data);
    if size(data,1) > 1, data = data(1,:); end
    
    % NEW, TRYING TO USE FOR PATIENT 2.
    MetaTags = NS6hdr.MetaTags;
    MetaTags.ChannelID = thisID;

    ElectrodesInfo = struct( ...
    'Type', 'CC', ...
    'ChannelID', thisID, ...
    'Label', sprintf('chan%d', thisID), ...
    'MaxDigiValue', int16(32764), ...
    'MinDigiValue', int16(-32764), ...
    'MaxAnalogValue', int16(8191), ...
    'MinAnalogValue', int16(-8191), ...
    'AnalogUnits', 'uV' ...
    );

    RawData = data;
    scalingFactor = 1;

    outFile = fullfile(outDir, sprintf('%s%d.mat', prefix, thisID));
    save(outFile,'data','RawData','MetaTags','ElectrodesInfo','scalingFactor','-v7.3');

    % OLD, USED I THINK FOR PATIENT 1.
    % Save one MAT per channel, named by original ChannelID
    % outFile = fullfile(outDir, sprintf('%s%d.mat', prefix, thisID));
    % scalingFactor = 1; %#ok<NASGU>  % keep var names OSort expects if needed
    % save(outFile, 'data', 'scalingFactor', '-v7.3');

    fprintf('Saved %s (ChannelID %d)\n', outFile, thisID);
end
